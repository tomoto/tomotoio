import logging as log
from enum import Enum
from math import atan2, cos, degrees, hypot, radians, sin
from threading import RLock
from typing import Optional, Tuple, cast

from .cube import Cube
from .data import PositionID
from .geo import *

MILLIS_PER_UNIT = 560.0 / 410.0
AXLE_TRACK_UNITS = 26.6 / MILLIS_PER_UNIT
MOTOR_DURATION = 1.5


class MatType(Enum):
    TOIO_COLLECTION_1 = 0
    TOIO_COLLECTION_2 = 1


class Mat:
    def __init__(self, matType: MatType = MatType.TOIO_COLLECTION_1):
        self.topLeft = Vector(45 + matType.value * 500, 45)
        self.bottomRight = Vector(455 + matType.value * 500, 455)
        self.center = self.topLeft.interpolate(self.bottomRight, 0.5)

    def margin(self, x: float, y: float) -> float:
        return min(x - self.topLeft.x, y - self.topLeft.y, self.bottomRight.x - x, self.bottomRight.y - y)


def calcRotateSpeed(da: float, currentSpeed: float, speedFactor: float) -> float:
    return max(min(currentSpeed + 5, abs(da) * speedFactor), 10) * (1 if da >= 0 else -1)


def calcMoveSpeed(distance: float, da: float, currentSpeed: float, maxSpeed: float, fixedSpeed: bool) -> Tuple[float, float]:
    if fixedSpeed:
        s = max(maxSpeed, 10)
    else:
        s = max(min(currentSpeed + 5, distance, maxSpeed), 10)

    if abs(da) > 0.01:
        rc = distance / 2 / sin(radians(abs(da)))
        k = max((rc + AXLE_TRACK_UNITS / 2) / (rc - AXLE_TRACK_UNITS / 2), 0)
    else:
        k = 1

    r = s * k
    if (r > 100):
        (s, r) = (s / (r / 100), 100)
    if da >= 0:
        return (r, s)
    else:
        return (s, r)


class NavigatorBase:
    def __init__(self, cube: Cube):
        self.cube = cube
        self.mat = Mat()


class NavigationCommandBase:
    def __init__(self, nav: NavigatorBase):
        self.nav = nav
        self.cube = nav.cube
        self.currentSpeed = 0.0
        self.complete = False
        self.lock = RLock()

    def handleNotification(self, e):
        raise NotImplementedError()


class RotateCommand(NavigationCommandBase):
    def __init__(self, nav: NavigatorBase, targetAngle: float, tolerance: float, rotateSpeedFactor: float = 0.5):
        super().__init__(nav)
        self.targetAngle = targetAngle
        self.tolerance = tolerance
        self.rotateSpeedFactor = rotateSpeedFactor

    def updateTarget(self, targetAngle: float, tolerance: float, rotateSpeedFactor: float = None):
        with self.lock:
            self.targetAngle = targetAngle
            self.tolerance = tolerance
            if rotateSpeedFactor is not None:
                self.rotateSpeedFactor = rotateSpeedFactor

    def handleNotification(self, e):
        with self.lock:
            if not isinstance(e, PositionID):
                return

            da = angleDiff(self.targetAngle - cast(PositionID, e).angle)
            if abs(da) < self.tolerance:
                self.complete = True
                self.currentSpeed = 0.0
                self.cube.setMotor(0, 0)
                return
            else:
                self.complete = False

            s = calcRotateSpeed(da, self.currentSpeed, self.rotateSpeedFactor)
            self.currentSpeed = abs(s)

            if abs(da) < 10 and self.tolerance < 6:
                # Precise mode (not always working well)
                self.cube.setMotor(s, -s, 0.02)
            else:
                # Normal mode
                self.cube.setMotor(s, -s, MOTOR_DURATION)


class MoveCommand(NavigationCommandBase):
    def __init__(self, nav: NavigatorBase, targetX: float, targetY: float, tolerance: float,
                 moveSpeed: float = 100, rotateSpeedFactor: float = 0.5,
                 moveRotateThreshold: float = 30, fixedSpeed: bool = False):
        super().__init__(nav)
        self.moveSpeed = moveSpeed
        self.rotateSpeedFactor = rotateSpeedFactor
        self.isMoving = False
        self.updateTarget(targetX, targetY, tolerance, moveSpeed, rotateSpeedFactor, moveRotateThreshold, fixedSpeed)

    def updateTarget(self, targetX: float, targetY: float, tolerance: float,
                     moveSpeed: float = None, rotateSpeedFactor: float = None,
                     moveRotateThreshold: float = None, fixedSpeed: bool = None):
        with self.lock:
            self.target = Vector(targetX, targetY)
            self.tolerance = tolerance
            if moveSpeed is not None:
                self.moveSpeed = moveSpeed
            if rotateSpeedFactor is not None:
                self.rotateSpeedFactor = rotateSpeedFactor
            if moveRotateThreshold is not None:
                self.moveRotateThreshold = moveRotateThreshold
            if fixedSpeed is not None:
                self.fixedSpeed = fixedSpeed

    def handleNotification(self, e):
        with self.lock:
            if not isinstance(e, PositionID):
                return

            v = self.target - Vector(e)
            da = angleDiff(v.direction() - cast(PositionID, e).angle)
            distance = v.magnitude()

            if distance < self.tolerance:
                self.complete = True
                self.currentSpeed = 0.0
                self.cube.setMotor(0, 0)
                return
            else:
                self.complete = False

            if self.isMoving:
                # Move
                if abs(da) > self.moveRotateThreshold:
                    self.isMoving = False
                    self.currentSpeed = 0.0
                    return

                (left, right) = calcMoveSpeed(distance, da, self.currentSpeed, self.moveSpeed, self.fixedSpeed)
                self.currentSpeed = min(left, right)
                self.cube.setMotor(left, right, MOTOR_DURATION)
            else:
                # Rotate
                if abs(da) < self.moveRotateThreshold:
                    self.isMoving = True
                    self.currentSpeed = 0.0
                    return

                s = calcRotateSpeed(da, self.currentSpeed, self.rotateSpeedFactor)
                self.currentSpeed = abs(s)
                self.cube.setMotor(s, -s, MOTOR_DURATION)


class CircleCommand(NavigationCommandBase):
    def __init__(self, nav: NavigatorBase, centerX: float, centerY: float, radius: float, moveSpeed: float = 100):
        super().__init__(nav)
        self.moveCommand = MoveCommand(nav, 0, 0, 0)
        self.moveSpeed = moveSpeed
        self.rotateDirection = 1
        self.updateTarget(centerX, centerY, radius)

    def updateTarget(self, centerX: float, centerY: float, radius: float, moveSpeed: float = None):
        self.center = Vector(centerX, centerY)
        self.radius = radius
        if moveSpeed is not None:
            self.moveSpeed = moveSpeed

    def handleNotification(self, e):
        with self.lock:
            if not isinstance(e, PositionID):
                return

            v = (Vector(e) - self.center).normalize()
            d = self.rotateDirection
            t = self.center + v.transform((1, -0.5 * d, 0.5 * d, 1)) * self.radius
            self.moveCommand.updateTarget(t.x, t.y, 0, moveSpeed=self.moveSpeed)
            self.moveCommand.handleNotification(e)

            if self.nav.mat.margin(t.x, t.y) < 10:
                self.rotateDirection *= -1


class Navigator(NavigatorBase):
    def __init__(self, cube: Cube):
        super().__init__(cube)
        self.lastPosition: Optional[PositionID] = None
        self.command: Optional[NavigationCommandBase] = None

        cube.toioID.addListener(self._handleNotification)
        cube.toioID.enableNotification()

    def _handleNotification(self, e):
        if isinstance(e, PositionID):
            self.lastPosition = e

        if self.command:
            self.command.handleNotification(e)

    def move(self, targetX: float, targetY: float, tolerance: float, moveRotateThreshold: float = 30, fixedSpeed: bool = False):
        if isinstance(self.command, MoveCommand):
            self.command.updateTarget(targetX, targetY, tolerance, moveRotateThreshold=moveRotateThreshold, fixedSpeed=fixedSpeed)
        else:
            self.setCommand(MoveCommand(self, targetX, targetY, tolerance, moveRotateThreshold=moveRotateThreshold, fixedSpeed=fixedSpeed))

    def rotate(self, targetAngle, tolerance):
        if isinstance(self.command, RotateCommand):
            self.command.updateTarget(targetAngle, tolerance)
        else:
            self.setCommand(RotateCommand(self, targetAngle, tolerance))

    def circle(self, centerX, centerY, radius):
        if isinstance(self.command, CircleCommand):
            self.command.updateTarget(centerX, centerY, radius)
        else:
            self.setCommand(CircleCommand(self, centerX, centerY, radius))

    def setCommand(self, command: Optional[NavigationCommandBase]):
        self.command = command
