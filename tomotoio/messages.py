import struct

from .data import *


def _raiseWrongBytesError(data):
    raise ValueError("Wrong bytes '%s'" % data)


def decodeToioID(data):
    if data[0] == 0x01:
        (_, x, y, a, sx, sy, sa) = struct.unpack("<BHHHHHH", data)
        return PositionID(x, y, a, sx, sy, sa)
    if data[0] == 0x02:
        (_, value, angle) = struct.unpack("<BIH", data)
        return StandardID(value, angle)
    else:
        if data[0] == 0x03:
            return MissedID(ToioIDType.POSITION)
        elif data[0] == 0x04:
            return MissedID(ToioIDType.STANDARD)

    _raiseWrongBytesError(data)


def decodeMotion(data):
    if data[0] == 0x01:
        (_, isLevel, collision) = struct.unpack("<BBB", data)
        return Motion(isLevel != 0, collision != 0)

    _raiseWrongBytesError(data)


def decodeButton(data):
    if data[0] == 0x01:
        (_, isPressed) = struct.unpack("<BB", data)
        return isPressed != 0

    _raiseWrongBytesError(data)


def decodeBattery(data):
    return int(data[0])


def _motorDirection(value):
    return 1 if value >= 0 else 2


def encodeMotor(left, right, duration=0):
    d = min(int(duration * 100), 255)
    return bytes([2, 1, _motorDirection(left), abs(left), 2, _motorDirection(right), abs(right), d])


def encodeLight(r, g, b, duration=0):
    return bytes([3, min(int(duration * 100), 255), 1, 1, r, g, b])


def encodeLightPattern(lights, repeat=0):
    b = list([4, repeat, len(lights)])
    for light in lights:
        b += [min(int(light.duration * 100), 255), 1, 1, light.r, light.g, light.b]
    return bytes(b)


def encodeTurnOffLight():
    return bytes([1])


def encodeSound(id, volume=255):
    return bytes([2, id, volume])


def encodeSoundByNotes(notes, repeat=0):
    b = list([3, repeat, len(notes)])
    for note in notes:
        b += [min(int(note.duration * 100), 255), note.noteNumber, note.volume]
    return bytes(b)


def encodeConfigProtocolVersionRequest():
    return bytes([1, 0])


def decodeConfigProtocolVersionResponse(data):
    if data[0] == 0x81:
        return data[2:].decode()
    _raiseWrongBytesError(data)


def encodeConfigLevelThreshold(angle=45):
    return bytes([5, min(angle, 45)])


def encodeConfigCollisionThreshold(value=7):
    return bytes([6, min(value, 10)])
