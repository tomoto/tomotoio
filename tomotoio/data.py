from enum import Enum


class ToioIDType(Enum):
    INVALID = 0
    POSITION = 1
    STANDARD = 2
    MISSED = 3


class ToioID:
    def __init__(self, type: ToioIDType):
        self.type = type

    def isPosition(self):
        return self.type == ToioIDType.POSITION

    def isStandard(self):
        return self.type == ToioIDType.STANDARD

    def isMissed(self):
        return self.type == ToioIDType.MISSED

    def __str__(self):
        return str(vars(self))


class PositionID(ToioID):
    def __init__(self, x: float, y: float, angle: float, sensorX: float, sensorY: float, sensorAngle: float):
        super().__init__(ToioIDType.POSITION)
        self.x = x
        self.y = y
        self.angle = angle
        self.sensorX = sensorX
        self.sensorY = sensorY
        self.sensorAngle = sensorAngle


class StandardID(ToioID):
    def __init__(self, value: float, angle: float):
        super().__init__(ToioIDType.STANDARD)
        self.value = value
        self.angle = angle


class MissedID(ToioID):
    def __init__(self, fromType: ToioIDType):
        super().__init__(ToioIDType.MISSED)
        self.fromType = fromType

class Orientation(Enum):
    INVALID = 0
    STRAIGHT_UP = 1
    BOTTOM_UP = 2
    BACK_UP = 3
    FRONT_UP = 4
    RIGHT_UP = 5
    LEFT_UP = 6

class Motion:
    def __init__(self, isLevel: bool, collision: bool, doubleTap: bool, orientation: Orientation):
        self.isLevel = isLevel
        self.collision = collision
        self.doubleTap = doubleTap
        self.orientation = orientation

    def __str__(self):
        return str(vars(self))


class Light:
    def __init__(self, r: int, g: int, b: int, duration: float):
        self.r = r
        self.g = g
        self.b = b
        self.duration = duration


class Note:
    REST = 128

    def __init__(self, noteNumber: int, duration: float, volume: int = 255):
        self.noteNumber = noteNumber
        self.duration = duration
        self.volume = volume
