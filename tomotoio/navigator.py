import logging as log
from math import atan2, cos, degrees, hypot, radians, sin
from threading import RLock

from .data import PositionID
from .geo import *

MILLIS_PER_UNIT = 560 / 410
AXLE_TRACK_UNITS = 26.6 / MILLIS_PER_UNIT
MOTOR_DURATION = 1.5


class Mat:
    def __init__(self, number=0):
        self.topLeft = Vector(45 + number * 500, 45)
        self.bottomRight = Vector(455 + number * 500, 455)
        self.center = self.topLeft.interpolate(self.bottomRight, 0.5)

    def margin(self, x, y):
        return min(x - self.topLeft.x, y - self.topLeft.y, self.bottomRight.x - x, self.bottomRight.y - y)


def calcRotateSpeed(da, currentSpeed, speedFactor):
    return max(min(currentSpeed + 5, abs(da) * speedFactor), 10) * (1 if da >= 0 else -1)


def calcMoveSpeed(distance, da, currentSpeed, maxSpeed, fixedSpeed):
    if fixedSpeed:
        s = fixedSpeed
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


class NavigationCommandBase:
    def __init__(self, nav):
        self.nav = nav
        self.cube = nav.cube
        self.currentSpeed = 0
        self.complete = False
        self.lock = RLock()


class RotateCommand(NavigationCommandBase):
    def __init__(self, nav, targetAngle, tolerance, rotateSpeedFactor=0.5):
        super().__init__(nav)
        self.targetAngle = targetAngle
        self.tolerance = tolerance
        self.rotateSpeedFactor = rotateSpeedFactor

    def updateTarget(self, targetAngle, tolerance=None):
        with self.lock:
            self.targetAngle = targetAngle
            if tolerance is not None:
                self.tolerance = tolerance

    def handleNotification(self, e):
        with self.lock:
            if not isinstance(e, PositionID):
                return

            da = angleDiff(self.targetAngle - e.angle)
            if abs(da) < self.tolerance:
                self.complete = True
                self.currentSpeed = 0
                self.cube.setMotor(0, 0)
                return
            else:
                self.complete = False

            s = calcRotateSpeed(da, self.currentSpeed, self.rotateSpeedFactor)
            self.currentSpeed = abs(s)

            if abs(da) < 10 and self.tolerance < 5:
                # Precise mode
                self.cube.setMotor(s, -s, 0.02)
            else:
                # Normal mode
                self.cube.setMotor(s, -s, MOTOR_DURATION)


class MoveCommand(NavigationCommandBase):
    def __init__(self, nav, targetX, targetY, tolerance=0, moveSpeed=100, rotateSpeedFactor=0.5, moveRotateThreshold=30, fixedSpeed=None):
        super().__init__(nav)
        self.moveSpeed = moveSpeed
        self.rotateSpeedFactor = rotateSpeedFactor
        self.isMoving = False
        self.updateTarget(targetX, targetY, tolerance, moveRotateThreshold, fixedSpeed)

    def updateTarget(self, targetX, targetY, tolerance=0, moveRotateThreshold=30, fixedSpeed=None):
        with self.lock:
            self.target = Vector(targetX, targetY)
            self.tolerance = tolerance
            self.moveRotateThreshold = moveRotateThreshold
            self.fixedSpeed = fixedSpeed

    def handleNotification(self, e):
        with self.lock:
            if not isinstance(e, PositionID):
                return

            v = self.target - Vector(e)
            da = angleDiff(v.direction() - e.angle)
            distance = v.magnitude()

            if distance < self.tolerance:
                self.complete = True
                self.currentSpeed = 0
                self.cube.setMotor(0, 0)
                return
            else:
                self.complete = False

            if self.isMoving:
                # Move
                if abs(da) > self.moveRotateThreshold:
                    self.isMoving = False
                    self.currentSpeed = 0
                    return

                (left, right) = calcMoveSpeed(distance, da, self.currentSpeed, self.moveSpeed, self.fixedSpeed)
                self.currentSpeed = min(left, right)
                self.cube.setMotor(left, right, MOTOR_DURATION)
            else:
                # Rotate
                if abs(da) < self.moveRotateThreshold:
                    self.isMoving = True
                    self.currentSpeed = 0
                    return

                s = calcRotateSpeed(da, self.currentSpeed, self.rotateSpeedFactor)
                self.currentSpeed = abs(s)
                self.cube.setMotor(s, -s, MOTOR_DURATION)


class CircleCommand(NavigationCommandBase):
    def __init__(self, nav, centerX, centerY, radius, moveSpeed=100):
        super().__init__(nav)
        self.moveCommand = MoveCommand(nav, None, None, moveSpeed=moveSpeed)
        self.rotateDirection = 1
        self.updateTarget(centerX, centerY, radius)

    def updateTarget(self, centerX, centerY, radius):
        self.center = Vector(centerX, centerY)
        self.radius = radius

    def handleNotification(self, e):
        with self.lock:
            if not isinstance(e, PositionID):
                return

            v = (Vector(e.x, e.y) - self.center).normalize()
            d = self.rotateDirection
            t = self.center + v.transform((1, -0.5 * d, 0.5 * d, 1)) * self.radius
            self.moveCommand.updateTarget(t.x, t.y, 0)
            self.moveCommand.handleNotification(e)

            if self.nav.mat.margin(t.x, t.y) < 10:
                self.rotateDirection *= -1


class Navigator:
    def __init__(self, cube):
        self.cube = cube
        self.lastPosition = None
        self.command = None
        self.mat = Mat()

        cube.toioID.addListener(self._handleNotification)
        cube.toioID.enableNotification()

    def _handleNotification(self, e):
        if isinstance(e, PositionID):
            self.lastPosition = e

        if self.command:
            self.command.handleNotification(e)

    def move(self, targetX, targetY, tolerance=0, moveRotateThreshold=30, fixedSpeed=None):
        if isinstance(self.command, MoveCommand):
            self.command.updateTarget(targetX, targetY, tolerance, moveRotateThreshold=moveRotateThreshold, fixedSpeed=fixedSpeed)
        else:
            self.setCommand(MoveCommand(self, targetX, targetY, tolerance=tolerance, moveRotateThreshold=moveRotateThreshold, fixedSpeed=fixedSpeed))

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

    def setCommand(self, command):
        self.command = command
