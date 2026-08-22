#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "component.h"

namespace py = pybind11;

namespace {

py::array_t<double> meter_array(py::object value) {
    if (py::hasattr(value, "to")) value = value.attr("to")("meter").attr("magnitude");
    return py::module_::import("numpy").attr("atleast_1d")(py::module_::import("numpy").attr("asarray")(value, py::arg("dtype") = "float64")).cast<py::array_t<double>>();
}

double meter(py::object value) {
    const auto values = meter_array(std::move(value));
    if (values.size() != 1) throw py::value_error("Expected one scalar length.");
    return *values.data();
}

py::object required(const py::kwargs& kwargs, const char* key) {
    if (!kwargs.contains(key)) throw py::type_error(std::string("Missing required keyword argument: ") + key);
    return kwargs[key];
}

py::object optional(const py::kwargs& kwargs, const char* key, py::object fallback) {
    return kwargs.contains(key) ? kwargs[key] : fallback;
}

class NativeComponent {
public:
    NativeComponent(py::object grid, py::tuple position, double epsilon_r, py::object sigma, py::object facecolor, py::object edgecolor, double alpha, double rotation)
        : grid_(std::move(grid)), epsilon_r_(epsilon_r), sigma_(std::move(sigma)), facecolor_(std::move(facecolor)), edgecolor_(std::move(edgecolor)), alpha_(alpha), rotation_(rotation) {
        if (position.size() != 2) throw py::value_error("position must contain exactly two coordinates.");
        coordinate_ = grid_.attr("get_coordinate")(py::arg("x") = position[0], py::arg("y") = position[1]);
    }
    virtual ~NativeComponent() = default;

    py::array_t<bool> mask() const {
        auto x = grid_.attr("x_stamp").attr("to")("meter").attr("magnitude").cast<py::array_t<double>>();
        auto y = grid_.attr("y_stamp").attr("to")("meter").attr("magnitude").cast<py::array_t<double>>();
        const auto xv = x.unchecked<1>(); const auto yv = y.unchecked<1>();
        py::array_t<bool> result({xv.shape(0), yv.shape(0)}); auto output = result.mutable_unchecked<2>();
        for (py::ssize_t i = 0; i < xv.shape(0); ++i)
            for (py::ssize_t j = 0; j < yv.shape(0); ++j)
                output(i, j) = contains(xv(i), yv(j));
        return result;
    }
    void add_to_epsilon_r_mesh(py::object mesh) const { mesh.attr("__setitem__")(mask(), epsilon_r_); }
    void add_to_sigma_mesh(py::object mesh) const { mesh.attr("__setitem__")(mask(), sigma_); }
    py::object add_non_linear_effect_to_field(py::object field) const { return field; }
    py::object add_to_ax(const py::object& ax) const {
        py::object x = grid_.attr("x_stamp").attr("to")("meter").attr("magnitude");
        py::object y = grid_.attr("y_stamp").attr("to")("meter").attr("magnitude");
        py::object component_mask = mask();
        py::object transposed_mask = component_mask.attr("T");
        return ax.attr("contourf")(x, y, transposed_mask, py::arg("levels") = py::make_tuple(0.5, 1.5), py::arg("colors") = py::make_tuple(facecolor_), py::arg("alpha") = alpha_);
    }
    void plot() const {
        auto pyplot = py::module_::import("matplotlib.pyplot"); auto items = pyplot.attr("subplots")(1, 1, py::arg("figsize") = py::make_tuple(6, 6)).cast<py::tuple>();
        py::object ax = items[1]; ax.attr("set_aspect")("equal"); add_to_ax(ax); pyplot.attr("show")();
    }
    py::object coordinate() const { return coordinate_; }
    double epsilon_r() const { return epsilon_r_; }
    py::array_t<bool> idx() const { return mask(); }

protected:
    virtual bool contains(double x, double y) const = 0;
    void local(double x, double y, double& lx, double& ly) const {
        const double center_x = meter(coordinate_.attr("x")); const double center_y = meter(coordinate_.attr("y"));
        const double dx = x - center_x, dy = y - center_y, radians = rotation_ * std::acos(-1.0) / 180.0;
        lx = std::cos(radians) * dx + std::sin(radians) * dy; ly = -std::sin(radians) * dx + std::cos(radians) * dy;
    }
    py::object grid_, coordinate_, sigma_, facecolor_, edgecolor_; double epsilon_r_, alpha_, rotation_;
};

class CircleElement final : public NativeComponent {
public: CircleElement(py::object grid, py::tuple position, double epsilon, double radius, py::object sigma, py::object face, py::object edge, double alpha, double rotation) : NativeComponent(std::move(grid), std::move(position), epsilon, std::move(sigma), std::move(face), std::move(edge), alpha, rotation), radius2_(radius * radius) { if (radius <= 0) throw py::value_error("radius must be positive."); }
protected: bool contains(double x, double y) const override { double lx, ly; local(x, y, lx, ly); return lx * lx + ly * ly <= radius2_; } private: double radius2_; };
class RectangleElement : public NativeComponent {
public: RectangleElement(py::object grid, py::tuple position, double epsilon, double width, double height, py::object sigma, py::object face, py::object edge, double alpha, double rotation) : NativeComponent(std::move(grid), std::move(position), epsilon, std::move(sigma), std::move(face), std::move(edge), alpha, rotation), hw_(width/2), hh_(height/2) { if(width<=0||height<=0) throw py::value_error("width and height must be positive."); }
protected: bool contains(double x,double y) const override { double lx,ly;local(x,y,lx,ly);return std::abs(lx)<=hw_&&std::abs(ly)<=hh_; } private: double hw_,hh_; };
class WaveguideElement final : public NativeComponent {
public: WaveguideElement(py::object grid,py::tuple p0,py::tuple p1,double epsilon,double width,py::object sigma,py::object face,py::object edge,double alpha,double rotation):NativeComponent(grid,p0,epsilon,std::move(sigma),std::move(face),std::move(edge),alpha,rotation),width2_(width*width){auto c0=grid.attr("get_coordinate")(py::arg("x")=p0[0],py::arg("y")=p0[1]);auto c1=grid.attr("get_coordinate")(py::arg("x")=p1[0],py::arg("y")=p1[1]);x0_=meter(c0.attr("x"));y0_=meter(c0.attr("y"));x1_=meter(c1.attr("x"));y1_=meter(c1.attr("y"));if(width<=0||std::hypot(x1_-x0_,y1_-y0_)==0)throw py::value_error("width must be positive and endpoints distinct.");}protected:bool contains(double x,double y)const override{double dx=x1_-x0_,dy=y1_-y0_,den=dx*dx+dy*dy,t=((x-x0_)*dx+(y-y0_)*dy)/den;t=std::clamp(t,0.,1.);double ex=x-(x0_+t*dx),ey=y-(y0_+t*dy);return ex*ex+ey*ey<=width2_*(0.25+1e-12);}private:double x0_,y0_,x1_,y1_,width2_;};
class EllipseElement final : public NativeComponent {
public: EllipseElement(py::object grid,py::tuple position,double epsilon,double width,double height,py::object sigma,py::object face,py::object edge,double alpha,double rotation) : NativeComponent(std::move(grid),std::move(position),epsilon,std::move(sigma),std::move(face),std::move(edge),alpha,rotation), iw_(4/(width*width)),ih_(4/(height*height)){if(width<=0||height<=0)throw py::value_error("width and height must be positive.");}
protected: bool contains(double x,double y) const override{double lx,ly;local(x,y,lx,ly);return lx*lx*iw_+ly*ly*ih_<=1.;}private:double iw_,ih_;};
class RingElement final : public NativeComponent {
public: RingElement(py::object grid,py::tuple position,double epsilon,double inner,double width,py::object sigma,py::object face,py::object edge,double alpha,double rotation):NativeComponent(std::move(grid),std::move(position),epsilon,std::move(sigma),std::move(face),std::move(edge),alpha,rotation),inner2_(inner*inner),outer2_((inner+width)*(inner+width)){if(inner<0||width<=0)throw py::value_error("inner_radius must be non-negative and width positive.");}protected:bool contains(double x,double y)const override{double lx,ly;local(x,y,lx,ly);double r2=lx*lx+ly*ly;return r2>=inner2_&&r2<=outer2_;}private:double inner2_,outer2_;};
class TriangleElement final : public NativeComponent {
public: TriangleElement(py::object grid,py::tuple position,double epsilon,double side,py::object sigma,py::object face,py::object edge,double alpha,double rotation):NativeComponent(std::move(grid),std::move(position),epsilon,std::move(sigma),std::move(face),std::move(edge),alpha,rotation),side_(side){if(side<=0)throw py::value_error("side_length must be positive.");}protected:bool contains(double x,double y)const override{double lx,ly;local(x,y,lx,ly);const double h=std::sqrt(3.)*side_/2.;return ly>=-h/3.&&ly<=2*h/3.&&std::abs(lx)<=side_*(2*h/3.-ly)/(2*h);}private:double side_;};
class LensElement final : public NativeComponent {
public: LensElement(py::object grid,py::tuple position,double epsilon,double curvature,double width,py::object sigma,py::object face,py::object edge,double alpha,double rotation):NativeComponent(std::move(grid),std::move(position),epsilon,std::move(sigma),std::move(face),std::move(edge),alpha,rotation),r2_(curvature*curvature),left_(std::abs(curvature)-width/2),right_(-std::abs(curvature)+width/2){if(curvature==0||width<=0||width>2*std::abs(curvature))throw py::value_error("width must be positive and no more than twice curvature.");}protected:bool contains(double x,double y)const override{double lx,ly;local(x,y,lx,ly);return (lx-left_)*(lx-left_)+ly*ly<=r2_&&(lx-right_)*(lx-right_)+ly*ly<=r2_;}private:double r2_,left_,right_;};
class GratingElement final : public NativeComponent { public: GratingElement(py::object grid,py::tuple position,double epsilon,double period,double duty,int periods,py::object sigma,py::object face,py::object edge,double alpha,double rotation):NativeComponent(std::move(grid),std::move(position),epsilon,std::move(sigma),std::move(face),std::move(edge),alpha,rotation),period_(period),duty_(duty),periods_(periods){if(period<=0||duty<=0||duty>1||periods<1)throw py::value_error("period must be positive, duty_cycle in (0, 1], and num_periods positive.");}protected:bool contains(double x,double y)const override{double lx,ly;local(x,y,lx,ly);if(std::abs(ly)>period_/2||lx<0)return false;int bar=static_cast<int>(lx/period_);return bar<periods_&&lx-bar*period_<=duty_*period_;}private:double period_,duty_;int periods_;};

template <typename Type, typename... Args>
std::shared_ptr<Type> make_element(Args&&... args) { return std::make_shared<Type>(std::forward<Args>(args)...); }

py::object sigma(const py::kwargs& k) {
    if (k.contains("sigma")) return k["sigma"];
    py::object ureg = py::module_::import("TypedUnit").attr("ureg");
    return py::float_(0.0) * ureg.attr("siemens") / ureg.attr("meter");
}
py::object face(const py::kwargs& k) { return optional(k, "facecolor", py::str("lightblue")); }
py::object edge(const py::kwargs& k) { return optional(k, "edgecolor", py::str("blue")); }
double alpha(const py::kwargs& k) { return optional(k, "alpha", py::float_(.3)).cast<double>(); }
double rotation(const py::kwargs& k) { return optional(k, "rotation", py::float_(0.)).cast<double>(); }

}  // namespace

PYBIND11_MODULE(components, module) {
    module.doc() = R"doc(
Native optical components for LightWave2D.

Components rasterize physical shapes onto a :class:`LightWave2D.grid.Grid` and
apply relative permittivity or conductivity to simulation meshes.
)doc";
    py::class_<NativeComponent, std::shared_ptr<NativeComponent>>(module, "BaseComponent", R"doc(
Base class for grid-rasterized optical components.

Notes
-----
Concrete components accept a ``grid``, physical position and material
properties. Their ``idx`` property is a Boolean mask with ``grid.shape``.
)doc")
        .def("add_to_epsilon_r_mesh", &NativeComponent::add_to_epsilon_r_mesh).def("add_to_sigma_mesh", &NativeComponent::add_to_sigma_mesh).def("add_non_linear_effect_to_field", &NativeComponent::add_non_linear_effect_to_field).def("add_to_ax", &NativeComponent::add_to_ax).def("plot", &NativeComponent::plot).def_property_readonly("idx", &NativeComponent::idx).def_property_readonly("coordinate", &NativeComponent::coordinate).def_property_readonly("epsilon_r", &NativeComponent::epsilon_r);
    py::class_<CircleElement, NativeComponent, std::shared_ptr<CircleElement>>(module, "Circle").def(py::init([](py::kwargs k){return make_element<CircleElement>(required(k,"grid"),required(k,"position").cast<py::tuple>(),required(k,"epsilon_r").cast<double>(),meter(required(k,"radius")),sigma(k),face(k),edge(k),alpha(k),rotation(k));}));
    py::class_<RectangleElement, NativeComponent, std::shared_ptr<RectangleElement>>(module, "Square").def(py::init([](py::kwargs k){double side=meter(required(k,"side_length"));return make_element<RectangleElement>(required(k,"grid"),required(k,"position").cast<py::tuple>(),required(k,"epsilon_r").cast<double>(),side,side,sigma(k),face(k),edge(k),alpha(k),rotation(k));}));
    py::class_<EllipseElement, NativeComponent, std::shared_ptr<EllipseElement>>(module, "Ellipse").def(py::init([](py::kwargs k){return make_element<EllipseElement>(required(k,"grid"),required(k,"position").cast<py::tuple>(),required(k,"epsilon_r").cast<double>(),meter(required(k,"width")),meter(required(k,"height")),sigma(k),face(k),edge(k),alpha(k),rotation(k));}));
    py::class_<TriangleElement, NativeComponent, std::shared_ptr<TriangleElement>>(module, "Triangle").def(py::init([](py::kwargs k){return make_element<TriangleElement>(required(k,"grid"),required(k,"position").cast<py::tuple>(),required(k,"epsilon_r").cast<double>(),meter(required(k,"side_length")),sigma(k),face(k),edge(k),alpha(k),rotation(k));}));
    py::class_<RingElement, NativeComponent, std::shared_ptr<RingElement>>(module, "RingResonator").def(py::init([](py::kwargs k){return make_element<RingElement>(required(k,"grid"),required(k,"position").cast<py::tuple>(),required(k,"epsilon_r").cast<double>(),meter(required(k,"inner_radius")),meter(required(k,"width")),sigma(k),face(k),edge(k),alpha(k),rotation(k));}));
    py::class_<LensElement, NativeComponent, std::shared_ptr<LensElement>>(module, "Lens").def(py::init([](py::kwargs k){return make_element<LensElement>(required(k,"grid"),required(k,"position").cast<py::tuple>(),required(k,"epsilon_r").cast<double>(),meter(required(k,"curvature")),meter(required(k,"width")),sigma(k),face(k),edge(k),alpha(k),rotation(k));}));
    py::class_<WaveguideElement, NativeComponent, std::shared_ptr<WaveguideElement>>(module, "Waveguide").def(py::init([](py::kwargs k){return make_element<WaveguideElement>(required(k,"grid"),required(k,"position_0").cast<py::tuple>(),required(k,"position_1").cast<py::tuple>(),required(k,"epsilon_r").cast<double>(),meter(required(k,"width")),sigma(k),face(k),edge(k),alpha(k),rotation(k));}));
    py::class_<GratingElement, NativeComponent, std::shared_ptr<GratingElement>>(module, "Grating").def(py::init([](py::kwargs k){return make_element<GratingElement>(required(k,"grid"),required(k,"position").cast<py::tuple>(),required(k,"epsilon_r").cast<double>(),meter(required(k,"period")),required(k,"duty_cycle").cast<double>(),required(k,"num_periods").cast<int>(),sigma(k),face(k),edge(k),alpha(k),rotation(k));}));
}
