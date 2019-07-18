from math import atan2, degrees, hypot
from numbers import Number


def direction(dx, dy):
    return degrees(atan2(dy, dx))


def angleDiff(da):
    return ((da + 180) % 360) - 180


class Vector:
    @staticmethod
    def isPointish(obj):
        return hasattr(obj, 'x') and hasattr(obj, 'y')

    def __init__(self, x, y=None):
        # dirty hack
        if self.isPointish(x):
            if y is None:
                self.x = x.x
                self.y = x.y
            elif self.isPointish(y):
                self.x = y.x - x.x
                self.y = y.y - x.y
        else:
            self.x = x
            self.y = y

    def __str__(self):
        return "[%f %f]" % (self.x, self.y)

    def magnitude(self):
        return hypot(self.x, self.y)

    def normalize(self, n=1.0):
        m = self.magnitude()
        if m == 0:
            return Vector(0, 0)
        else:
            return Vector(self.x / m * n, self.y / m * n)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, n):
        return Vector(self.x * n, self.y * n)

    def interpolate(self, other, n):
        return Vector(self.x * (1 - n) + other.x * n, self.y * (1 - n) + other.y * n)

    def transform(self, m):
        return Vector(self.x * m[0] + self.y * m[1], self.x * m[2] + self.y * m[3])

    def direction(self):
        return direction(self.x, self.y)
