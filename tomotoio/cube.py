from collections import defaultdict
from time import sleep
from typing import Any, Callable, Dict, Generic, TypeVar, Union
from bluepy.btle import UUID

from .constants import UUIDs
from .messages import *

PeerListenerFunc = Callable[[UUID, bytes], Any]


class Peer:
    def disconnect(self):
        raise NotImplementedError()

    def read(self, handle: int) -> bytes:
        raise NotImplementedError()

    def write(self, uuid: UUID, data: bytes, withResponse=False):
        raise NotImplementedError()

    def enableNotification(self, uuid: UUID, value: bool):
        raise NotImplementedError()

    def addListener(self, listener: PeerListenerFunc):
        raise NotImplementedError()


T = TypeVar('T')
CubeListenerFunc = Callable[[Any], Any]


class ReadableProperty(Generic[T]):
    def __init__(self, cube: 'Cube', uuid: UUID, decoder: Callable[[bytes], T]):
        self.cube = cube
        self.uuid = uuid
        self.decoder = decoder

    def get(self) -> T:
        return self.decoder(self.cube.peer.read(self.uuid))

    def enableNotification(self, value=True):
        self.cube.peer.enableNotification(self.uuid, value)

    def addListener(self, listener: CubeListenerFunc):
        self.cube.addListener(self.uuid, listener)


class Cube:
    def __init__(self, peer: Peer, name: str):
        self.peer = peer
        self.name = name
        self.listeners: Dict[int, List[CubeListenerFunc]] = defaultdict(lambda: list())
        self.toioID = ReadableProperty[Union[PositionID, StandardID, MissedID]](self, UUIDs.TOIO_ID, decodeToioID)
        self.motion = ReadableProperty[Motion](self, UUIDs.MOTION, decodeMotion)
        self.button = ReadableProperty[bool](self, UUIDs.BUTTON, decodeButton)
        self.battery = ReadableProperty[int](self, UUIDs.BATTERY, decodeBattery)

        peer.addListener(self._handleNotification)

    def _read(self, uuid: UUID) -> bytes:
        return self.peer.read(uuid)

    def _write(self, uuid: UUID, data: bytes, withResponse: bool = False):
        self.peer.write(uuid, data, withResponse)

    def _enableNotification(self, uuid: UUID, value: bool = True):
        self.peer.enableNotification(uuid, value)

    def _handleNotification(self, uuid: UUID, data: bytes):
        e: Any
        if uuid == UUIDs.MOTION:
            e = decodeMotion(data)
        elif uuid == UUIDs.BUTTON:
            e = decodeButton(data)
        elif uuid == UUIDs.TOIO_ID:
            e = decodeToioID(data)
        else:
            e = data

        for listener in self.listeners[uuid]:
            listener(e)

    def release(self):
        self.peer.disconnect()

    def addListener(self, uuid: UUID, listener: CubeListenerFunc):
        self.listeners[uuid].append(listener)

    def getConfigProtocolVersion(self) -> str:
        self._write(UUIDs.CONFIG, encodeConfigProtocolVersionRequest(), True)
        sleep(0.1)
        return decodeConfigProtocolVersionResponse(self._read(UUIDs.CONFIG))

    def setMotor(self, left: float, right: float, duration: float = 0):
        self._write(UUIDs.MOTOR, encodeMotor(int(left), int(right), duration))

    def setLight(self, r: int, g: int, b: int, duration: float = 0):
        self._write(UUIDs.LIGHT, encodeLight(r, g, b, duration))

    def setLightPattern(self, lights: List[Light], repeat: int = 0):
        self._write(UUIDs.LIGHT, encodeLightPattern(lights, repeat))

    def setSoundEffect(self, id: int, volume: int = 255):
        self._write(UUIDs.SOUND, encodeSound(id, volume))

    def setMusic(self, notes: List[Note], repeat=0):
        self._write(UUIDs.SOUND, encodeSoundByNotes(notes, repeat))

    def setConfigCollisionThreshold(self, value: int):
        self._write(UUIDs.CONFIG, encodeConfigCollisionThreshold(value))

    def setConfigLevelThreshold(self, angle: int):
        self._write(UUIDs.CONFIG, encodeConfigLevelThreshold(angle))

    def setConfigDoubleTapTiming(self, value: int):
        self._write(UUIDs.CONFIG, encodeConfigDoubleTapTiming(value))
