#pragma once

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <vector>

/** @brief Row-major Boolean raster mask for a component sampled on grid axes. */
struct Mask {
    std::size_t nx;
    std::size_t ny;
    std::vector<std::uint8_t> values;
};

/** @brief Abstract geometric primitive that rasterizes onto Cartesian axes. */
class Component {
public:
    explicit Component(double rotation_degrees = 0.0)
        : rotation_radians_(rotation_degrees * std::acos(-1.0) / 180.0) {}
    virtual ~Component() = default;

    /** @brief Evaluate containment at every coordinate pair and return a mask. */
    Mask rasterize(const std::vector<double>& x_coordinates, const std::vector<double>& y_coordinates) const;

protected:
    virtual bool contains(double x, double y) const = 0;
    void to_local_coordinates(double x, double y, double center_x, double center_y, double& local_x, double& local_y) const;

    double rotation_radians_;
};

/** @brief Circular primitive specified by centre coordinates and radius. */
class Circle final : public Component {
public:
    Circle(double center_x, double center_y, double radius);

protected:
    bool contains(double x, double y) const override;

private:
    double center_x_;
    double center_y_;
    double radius_squared_;
};

/** @brief Rotatable rectangular primitive specified by centre, width, and height. */
class Rectangle final : public Component {
public:
    Rectangle(double center_x, double center_y, double width, double height, double rotation_degrees = 0.0);

protected:
    bool contains(double x, double y) const override;

private:
    double center_x_;
    double center_y_;
    double half_width_;
    double half_height_;
};

/** @brief Rotatable elliptical primitive specified by centre, width, and height. */
class Ellipse final : public Component {
public:
    Ellipse(double center_x, double center_y, double width, double height, double rotation_degrees = 0.0);

protected:
    bool contains(double x, double y) const override;

private:
    double center_x_;
    double center_y_;
    double inverse_half_width_squared_;
    double inverse_half_height_squared_;
};

/** @brief Symmetric circular-arc lens primitive. */
class Lens final : public Component {
public:
    Lens(double center_x, double center_y, double curvature, double width, double rotation_degrees = 0.0);

protected:
    bool contains(double x, double y) const override;

private:
    double center_x_;
    double center_y_;
    double left_center_x_;
    double right_center_x_;
    double radius_squared_;
};
