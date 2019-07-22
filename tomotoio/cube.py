from collections import defaultdict
from time import sleep
from typing import Any, Callable, Dict, Generic, TypeVar, Union

from .constants import Handles
from .messages import *

PeerListenerFunc = Callable[[int, bytes], Any]


class Peer:
    def disconnect(self):
        raise NotImplementedError()

    def read(self, handle: int) -> bytes:
        raise NotImplementedError()

    def write(self, handle: int, data: bytes, withResponse=False):
        raise NotImplementedError()

    def enableNotification(self, handle: int, value: bool):
        raise NotImplementedError()

    def addListener(self, listener: PeerListenerFunc):
        raise NotImplementedError()


T = TypeVar('T')
CubeListenerFunc = Callable[[Any], Any]


class ReadableProperty(Generic[T]):
    def __init__(self, cube: 'Cube', handle: int, decoder: Callable[[bytes], T]):
        self.cube = cube
        self.handle = handle
        self.decoder = decoder

    def get(self) -> T:
        return self.decoder(self.cube.peer.read(self.handle))

    def enableNotification(self, value=True):
        self.cube.peer.enableNotification(self.handle, value)

    def addListener(self, listener: CubeListenerFunc):
        self.cube.addListener(self.handle, listener)


class Cube:
    def __init__(self, peer: Peer, name: str):
        self.peer = peer
        self.name = name
        self.listeners: Dict[int, List[CubeListenerFunc]] = defaultdict(lambda: list())
        self.toioID = ReadableProperty[Union[PositionID, StandardID, MissedID]](self, Handles.TOIO_ID, decodeToioID)
        self.motion = ReadableProperty[Motion](self, Handles.MOTION, decodeMotion)
        self.button = ReadableProperty[bool](self, Handles.BUTTON, decodeButton)
        self.battery = ReadableProperty[int](self, Handles.BATTERY, decodeBattery)

        peer.addListener(self._handleNotification)

    def _read(self, handle: int) -> bytes:
        return self.peer.read(handle)

    def _write(self, handle: int, data: bytes, withResponse: bool = False):
        self.peer.write(handle, data, withResponse)

    def _enableNotification(self, handle: int, value: bool = True):
        self.peer.enableNotification(handle, value)

    def _handleNotification(self, handle: int, data: bytes):
        e: Any
        if handle == Handles.MOTION:
            e = decodeMotion(data)
        elif handle == Handles.BUTTON:
            e = decodeButton(data)
        elif handle == Handles.TOIO_ID:
            e = decodeToioID(data)
        else:
            e = data

        for listener in self.listeners[handle]:
            listener(e)

    def release(self):
        self.peer.disconnect()

    def addListener(self, handle: int, listener: CubeListenerFunc):
        self.listeners[handle].append(listener)

    def getConfigProtocolVersion(self) -> str:
        self._write(Handles.CONFIG, encodeConfigProtocolVersionRequest(), True)
        sleep(0.1)
        return decodeConfigProtocolVersionResponse(self._read(Handles.CONFIG))

    def setMotor(self, left: float, right: float, duration: float = 0):
        self._write(Handles.MOTOR, encodeMotor(int(left), int(right), duration))

    def setLight(self, r: int, g: int, b: int, duration: float = 0):
        self._write(Handles.LIGHT, encodeLight(r, g, b, duration))

    def setLightPattern(self, lights: List[Light], repeat: int = 0):
        self._write(Handles.LIGHT, encodeLightPattern(lights, repeat))

    def setSoundEffect(self, id: int, volume: int = 255):
        self._write(Handles.SOUND, encodeSound(id, volume))

    def setMusic(self, notes: List[Note], repeat=0):
        self._write(Handles.SOUND, encodeSoundByNotes(notes, repeat))

    def setConfigCollisionThreshold(self, value: int):
        self._write(Handles.CONFIG, encodeConfigCollisionThreshold(value))

    def setConfigLevelThreshold(self, angle: int):
        self._write(Handles.CONFIG, encodeConfigLevelThreshold(angle))
