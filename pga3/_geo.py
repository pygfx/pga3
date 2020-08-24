"""
The API for handling geometry.
"""

import math


from ._algebra import (
    geometric_product,
    regressive_product,
    outer_product,
    inner_product,
    sandwich_product,
    conjugate,
    reverse,
)


# todo: Perfomance of matrix multiplications vs scale/translate/quaternion vs dual quaternions
# todo: Transform.to_matrix
# todo: Can we do nonisotropic scaling?
# todo: subclasses for each kind (Point/Line/Plane) or can we derive it from the value (even with roundof errors)?
# todo: use sparse representations (4 floats for points and planes), 8 for motors, etc.
# todo: everything from 2D PGA applies to 3D PGA (or 4D PGA) as well. So we could provide a 2D geometry too nearly for free?


class Algebra:
    """ Base class for a 3D projecive geometric algebra (PGA)
    """

    def __init__(self, value):
        assert isinstance(value, tuple) and len(value) == 16
        self._value = value

    @property
    def value(self):
        return self._value

    def __invert__(self):
        return Algebra(reverse(self.value))

    # todo: replace this with @, leaving * for scalar multiplications?
    def __mul__(self, other):
        """ The geometric product *.
        """
        if isinstance(other, (float, int)):
            return Algebra(tuple(x * other for x in self.value))
        assert isinstance(other, Algebra)
        value = geometric_product(self.value, other.value)
        return Algebra(value)

    def __rmul__(self, other):
        """ The geometric product *.
        """
        if isinstance(other, (float, int)):
            return Algebra(tuple(x * other for x in self.value))
        else:
            raise TypeError("Cannot multiply ....")

    def __xor__(self, other):
        """ The outer product ^ is the meet operation.
        """
        assert isinstance(other, Algebra)
        value = outer_product(self.value, other.value)
        return Algebra(value)

    def __and__(self, other):
        """ The regressive product & is the join operation.
        """
        assert isinstance(other, Algebra)
        value = regressive_product(self.value, other.value)
        return Algebra(value)

    def __or__(self, other):
        """ The inner product | is the inner product.
        """
        assert isinstance(other, Algebra)
        value = inner_product(self.value, other.value)
        return Algebra(value)

    def norm(self):
        self_ = Algebra(conjugate(self.value))
        return abs((self * self_).value[0]) ** 0.5

    def normalized(self):
        return self * (1 / self.norm())


# %% Geometric objects in 3D space


class Point(Algebra):
    def __init__(self, x=0, y=0, z=0):
        self._value = x, y, z

    def __repr__(self):
        return f"<Point {self._value}>"

    def get_line_to(self, point):
        """ join the points into a line.
        """
        assert isinstance(point, Point)
        return Line(regressive_product(self.value, point.value))

    @property
    def value(self):
        x, y, z = self._value
        return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, z, y, x, 1, 0)

    def project_onto(self, other):
        # Other can be a line or a plane
        value1 = self.value
        value2 = other.value
        value = geometric_product(inner_product(value1, value2), value2)
        z, y, x, w = value[11:15]
        return Point(x / w, y / w, z / w)


class Direction(Algebra):
    # This is an "ideal point". Ideal means infinite or in infinity. Not-ideal is called Eucledian.
    # todo: this is really a Point with w = 0, use the same class?

    def __init__(self, x=0, y=0, z=0):
        self._value = x, y, z

    def __repr__(self):
        return f"<Direction {self._value}>"

    @property
    def value(self):
        x, y, z = self._value
        return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, z, y, x, 0, 0)


class Line(Algebra):

    # todo: describe (in repr?) when it's an ideal line

    def __repr__(self):
        return f"<Line {self._value}>"

    @classmethod
    def from_xyz(cls, dx, dy, dz):
        point1 = Point(0, 0, 0)
        point2 = Point(dx, dy, dz)
        value = regressive_product(point1.value, point2.value)  # joint points in line
        return Line(value)

    @classmethod
    def from_points(cls, point1, point2):
        assert isinstance(point1, Point)
        assert isinstance(point2, Point)
        value = regressive_product(point1.value, point2.value)
        return Line(value)

    def project_onto(self, other):
        # Other can be a point or a plane
        value1 = self.value
        value2 = other.value
        value = geometric_product(inner_product(value1, value2), value2)
        return Line(value)


class Plane(Algebra):

    # todo: describe when it's an ideal line

    def __repr__(self):
        d, a, b, c = self._value[:4]
        value = a, b, c, d
        return f"<Plane algebra: abcd={value}>"

    @classmethod
    def from_abcd(cls, a, b, c, d):
        value = 0, d, a, b, c, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        return Plane(value)

    @classmethod
    def from_line_and_point(cls, line1, line2):
        pass

    @classmethod
    def from_points(cls, point1, point2, point3):
        assert isinstance(point1, Point)
        assert isinstance(point2, Point)
        assert isinstance(point3, Point)
        value = regressive_product(
            regressive_product(point1.value, point2.value), point3.value
        )
        return Plane(value)

    def project_onto(self, other):
        # Other can be a point or a line
        value1 = self.value
        value2 = other.value
        value = geometric_product(inner_product(value1, value2), value2)
        return Plane(value)


# %% Transformations


class Transform(Algebra):
    # Maybe call this Motor, as the Math people do?

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            return Transform(tuple(x * other for x in self.value))
        assert isinstance(other, Transform)
        value = geometric_product(self.value, other.value)
        return Transform(value)

    def as_matrix(self):
        """ Represent this transform as a 4x4 matrix.
        """
        # todo: is this possible????
        pass

    def project(self, a):
        assert isinstance(a, Point)  # todo: also allow planes, lines, etc.
        value = sandwich_product(self.value, a.value)
        return Point(*reversed(value[11:14]))


class Translator(Transform):

    # Remember, a translation in 2D PGA is a rotation around an ideal point/line.
    # And a translation at infinity is a rotation. Duality!
    # todo: Motors just need 8 values to represent, and thus their multiplications can also be simplified!

    @classmethod
    def from_xyz(cls, dx, dy, dz):
        half_distance = 0.5 * (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
        plane0 = Plane.from_abcd(0, 0, 0, 1)
        plane1 = Plane.from_abcd(dx, dy, dz, 0).normalized()
        line = plane1 * plane0  # must be an ideal line, therefore we use planes
        values = [half_distance * x for x in line.value]
        values[0] += 1.0
        return Translator(tuple(values))


class Rotor(Transform):
    @classmethod
    def from_angle_and_line(cls, angle, line):
        value = line.normalized().value
        value = [math.sin(angle / 2.0) * x for x in value]
        value[0] += math.cos(angle / 2.0)
        return Rotor(Algebra(tuple(value)).value)


# todo: can we do this (isotropic)? What about anisotropic scaling?
class Scalor(Transform):
    def __init__(self, scale):
        self._value = float(scale)

    @property
    def value(self):
        s = self._value ** 0.5
        return s, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
