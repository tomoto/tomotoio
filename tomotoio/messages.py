"""Decoder/encoder functions for Toio BLE communication messages"""

from struct import pack, unpack
from typing import List, Union
import logging

from .data import *


def _wrongBytesError(data: bytes) -> ValueError:
    raise ValueError("Wrong bytes '%s'" % data)


def decodeToioID(data: bytes) -> Union[PositionID, StandardID, MissedID]:
    if data[0] == 0x01:
        (_, x, y, a, sx, sy, sa) = unpack("<BHHHHHH", data)
        return PositionID(x, y, a, sx, sy, sa)
    if data[0] == 0x02:
        (_, value, angle) = unpack("<BIH", data)
        return StandardID(value, angle)
    if data[0] == 0x03:
        return MissedID(ToioIDType.POSITION)
    if data[0] == 0x04:
        return MissedID(ToioIDType.STANDARD)
    if data[0] == 0xff:
        return MissedID(ToioIDType.INVALID)

    raise _wrongBytesError(data)


def decodeMotion(data: bytes) -> Motion:
    if data[0] == 0x01:
        if len(data) == 3:
            (_, isLevel, collision) = unpack("<BBB", data)
            return Motion(isLevel != 0, collision != 0, 0, 0)
        else:
            (_, isLevel, collision, doubleTap, orientation) = unpack("<BBBBB", data)
            return Motion(isLevel != 0, collision != 0, doubleTap != 0, Orientation(orientation))

    raise _wrongBytesError(data)


def decodeButton(data: bytes) -> bool:
    if data[0] == 0x01:
        (_, isPressed) = unpack("<BB", data)
        return isPressed != 0

    raise _wrongBytesError(data)


def decodeBattery(data: bytes) -> int:
    return unpack("<B", data)[0]


def _motorDirection(value: int) -> int:
    return 1 if value >= 0 else 2


def encodeMotor(left: int, right: int, duration: float = 0) -> bytes:
    d = min(int(duration * 100), 255)
    return bytes([2, 1, _motorDirection(left), abs(left), 2, _motorDirection(right), abs(right), d])


def encodeLight(r: int, g: int, b: int, duration: float = 0) -> bytes:
    return bytes([3, min(int(duration * 100), 255), 1, 1, r, g, b])


def encodeLightPattern(lights: List[Light], repeat: int = 0) -> bytes:
    b = list([4, repeat, len(lights)])
    for light in lights:
        b += [min(int(light.duration * 100), 255), 1, 1, light.r, light.g, light.b]
    return bytes(b)


def encodeLightOff() -> bytes:
    return bytes([1])


def encodeSound(id: int, volume: int = 255) -> bytes:
    return bytes([2, id, volume])


def encodeSoundByNotes(notes: List[Note], repeat: int = 0) -> bytes:
    b = list([3, repeat, len(notes)])
    for note in notes:
        b += [min(int(note.duration * 100), 255), note.noteNumber, note.volume]
    return bytes(b)


def encodeSoundOff() -> bytes:
    return bytes([1])


def encodeConfigProtocolVersionRequest() -> bytes:
    return bytes([1, 0])


def decodeConfigProtocolVersionResponse(data: bytes) -> str:
    if data[0] == 0x81:
        return data[2:].decode()
    raise _wrongBytesError(data)


def encodeConfigLevelThreshold(angle: int = 45) -> bytes:
    return bytes([5, min(angle, 45)])


def encodeConfigCollisionThreshold(value: int = 7) -> bytes:
    return bytes([6, min(value, 10)])
