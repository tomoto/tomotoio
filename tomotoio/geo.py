from math import atan2, degrees, hypot
from numbers import Number
from typing import Any


def direction(dx: float, dy: float) -> float:
    """Returns the angle in degrees from (0, 0) to (dx, dy).

    Note, in the Toio coordinate system, the angle starts from east and increments clockwise.
    (i.e. east=0, south=90, west=180, north=270)

    Arguments:
        dx {float} -- X difference (left to right)
        dy {float} -- Y difference (top to bottom)

    Returns:
        float -- Angle in degrees
    """
    return degrees(atan2(dy, dx))


def angleDiff(da: float) -> float:
    """Fits the angle difference into [-180, 180)

    Arguments:
        da {float} -- Angle difference

    Returns:
        float -- Angle difference fit in [-180, 180)
    """
    return ((da + 180) % 360) - 180


class Vector:
    @staticmethod
    def isPointish(obj: Any):
        return hasattr(obj, 'x') and hasattr(obj, 'y')

    def __init__(self, x: Any, y: Any = None):
        """Creates a vector.

        Vector(x: float, y: float) -- from (x, y)
        Vector(p: Point-ish) -- from an object that has x and y as its properties
        Vector(p1: Point-ish, p2: Point-ish) -- from two objects that have x and y properties
        """
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

    def __str__(self) -> str:
        return "[%f %f]" % (self.x, self.y)

    def magnitude(self) -> float:
        return hypot(self.x, self.y)

    def normalize(self, n=1.0) -> 'Vector':
        m = self.magnitude()
        if m == 0:
            return Vector(0, 0)
        else:
            return Vector(self.x / m * n, self.y / m * n)

    def __add__(self, other) -> 'Vector':
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> 'Vector':
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, n) -> 'Vector':
        return Vector(self.x * n, self.y * n)

    def interpolate(self, other, n) -> 'Vector':
        return Vector(self.x * (1 - n) + other.x * n, self.y * (1 - n) + other.y * n)

    def transform(self, m) -> 'Vector':
        return Vector(self.x * m[0] + self.y * m[1], self.x * m[2] + self.y * m[3])

    def direction(self) -> float:
        return direction(self.x, self.y)

    def angle(self, target) -> float:
        return angleDiff(target.direction() - self.direction())
