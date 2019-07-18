from enum import Enum


class ToioIDType(Enum):
    POSITION = 1
    STANDARD = 2
    MISSED = 3


class ToioID:
    def __init__(self, type):
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
    def __init__(self, x, y, angle, sensorX, sensorY, sensorAngle):
        super().__init__(ToioIDType.POSITION)
        self.x = x
        self.y = y
        self.angle = angle
        self.sensorX = sensorX
        self.sensorY = sensorY
        self.sensorAngle = sensorAngle


class StandardID(ToioID):
    def __init__(self, value, angle):
        super().__init__(ToioIDType.STANDARD)
        self.type = ToioIDType.STANDARD
        self.value = value
        self.angle = angle


class MissedID(ToioID):
    def __init__(self, fromType):
        super().__init__(ToioIDType.MISSED)
        self.fromType = fromType


class Motion:
    def __init__(self, isLevel, collision):
        self.isLevel = isLevel
        self.collision = collision

    def __str__(self):
        return str(vars(self))


class Light:
    def __init__(self, r, g, b, duration):
        self.r = r
        self.g = g
        self.b = b
        self.duration = duration


class Note:
    REST = 128

    def __init__(self, noteNumber, duration, volume=255):
        self.noteNumber = noteNumber
        self.duration = duration
        self.volume = volume
