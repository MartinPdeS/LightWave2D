#include "component.h"

#include <algorithm>
#include <stdexcept>

Mask Component::rasterize(const std::vector<double>& x_coordinates, const std::vector<double>& y_coordinates) const
{
    Mask mask{x_coordinates.size(), y_coordinates.size(), std::vector<std::uint8_t>(x_coordinates.size() * y_coordinates.size(), 0)};

    for (std::size_t i = 0; i < mask.nx; ++i)
        for (std::size_t j = 0; j < mask.ny; ++j)
            mask.values[i * mask.ny + j] = static_cast<std::uint8_t>(contains(x_coordinates[i], y_coordinates[j]));

    return mask;
}

void Component::to_local_coordinates(double x, double y, double center_x, double center_y, double& local_x, double& local_y) const
{
    const double dx = x - center_x;
    const double dy = y - center_y;
    const double cosine = std::cos(rotation_radians_);
    const double sine = std::sin(rotation_radians_);
    local_x = cosine * dx + sine * dy;
    local_y = -sine * dx + cosine * dy;
}

Circle::Circle(double center_x, double center_y, double radius)
    : center_x_(center_x), center_y_(center_y), radius_squared_(radius * radius)
{
    if (radius <= 0.0)
        throw std::invalid_argument("Circle radius must be positive.");
}

bool Circle::contains(double x, double y) const
{
    const double dx = x - center_x_;
    const double dy = y - center_y_;
    return dx * dx + dy * dy <= radius_squared_;
}

Rectangle::Rectangle(double center_x, double center_y, double width, double height, double rotation_degrees)
    : Component(rotation_degrees), center_x_(center_x), center_y_(center_y), half_width_(width / 2.0), half_height_(height / 2.0)
{
    if (width <= 0.0 || height <= 0.0)
        throw std::invalid_argument("Rectangle width and height must be positive.");
}

bool Rectangle::contains(double x, double y) const
{
    double local_x;
    double local_y;
    to_local_coordinates(x, y, center_x_, center_y_, local_x, local_y);
    return std::abs(local_x) <= half_width_ && std::abs(local_y) <= half_height_;
}

Ellipse::Ellipse(double center_x, double center_y, double width, double height, double rotation_degrees)
    : Component(rotation_degrees), center_x_(center_x), center_y_(center_y), inverse_half_width_squared_(4.0 / (width * width)), inverse_half_height_squared_(4.0 / (height * height))
{
    if (width <= 0.0 || height <= 0.0)
        throw std::invalid_argument("Ellipse width and height must be positive.");
}

bool Ellipse::contains(double x, double y) const
{
    double local_x;
    double local_y;
    to_local_coordinates(x, y, center_x_, center_y_, local_x, local_y);
    return local_x * local_x * inverse_half_width_squared_ + local_y * local_y * inverse_half_height_squared_ <= 1.0;
}

Lens::Lens(double center_x, double center_y, double curvature, double width, double rotation_degrees)
    : Component(rotation_degrees), center_x_(center_x), center_y_(center_y), radius_squared_(curvature * curvature)
{
    const double radius = std::abs(curvature);
    if (radius <= 0.0 || width <= 0.0 || width > 2.0 * radius)
        throw std::invalid_argument("Lens width must be positive and no greater than twice its curvature.");

    left_center_x_ = radius - width / 2.0;
    right_center_x_ = -radius + width / 2.0;
}

bool Lens::contains(double x, double y) const
{
    double local_x;
    double local_y;
    to_local_coordinates(x, y, center_x_, center_y_, local_x, local_y);
    const double left_dx = local_x - left_center_x_;
    const double right_dx = local_x - right_center_x_;
    return left_dx * left_dx + local_y * local_y <= radius_squared_
        && right_dx * right_dx + local_y * local_y <= radius_squared_;
}
