import math

from pga3 import Point, Line, Plane, Translator, Rotor


# Define 3 points
p0 = Point(0, 0, 0)
p1 = Point(2, 3, 4)
p2 = Point(20, 3, 7)
p3 = Point(9, 12, 17)

# Three lines that connect these points
line1 = Line.from_points(p1, p2)
line2 = Line.from_points(p2, p3)
line3 = Line.from_points(p3, p1)

# A plane going through these points
plane1 = Plane.from_points(p1, p2, p3)

# Define a rotation and rotation
t = Translator.from_xyz(3, 0, 0)
r = Rotor.from_angle_and_line(math.pi / 2, Line.from_xyz(0, 0, 1))

# Transformations can be composed, of course
m = t * r

print(f"p1 = {p1}")
print(f"p2 = {p2}")
print(f"line1 = {line1}")
print(f"plane1 = {plane1}")

print("p1 translated", t.project(p1))
print("p1 translated + rotated", m.project(p1))

print("p1 projected onto line p1-p2", p1.project_onto(line3))
print("plane projected onto origin", plane1.project_onto(p0))


# todo: intersections, getting orthogonal planes/lines, getting ideal lines/points (i.e. directions)
# todo: metrics like distances and angles.
