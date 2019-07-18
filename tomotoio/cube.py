import logging as log
from collections import defaultdict
from time import sleep

from .constants import Handles
from .messages import * # decodeXxx's and encodeXxx's


class Cube:
    class ReadableProperty:
        def __init__(self, cube, handle, decoder):
            self.cube = cube
            self.handle = handle
            self.decoder = decoder

        def get(self):
            return self.decoder(self.cube.peer.read(self.handle))

        def enableNotification(self, value=True):
            self.cube.peer.enableNotification(self.handle, value)

        def addListener(self, listener):
            self.cube.addListener(self.handle, listener)

    def __init__(self, peer):
        self.peer = peer
        self.listeners = defaultdict(lambda: [])
        self.toioID = self.ReadableProperty(self, Handles.TOIO_ID, decodeToioID)
        self.motion = self.ReadableProperty(self, Handles.MOTION, decodeMotion)
        self.button = self.ReadableProperty(self, Handles.BUTTON, decodeButton)
        self.battery = self.ReadableProperty(self, Handles.BATTERY, decodeBattery)

        peer.addListener(self._handleNotification)

    def _read(self, handle):
        return self.peer.read(handle)

    def _write(self, handle, data, withResponse=False):
        self.peer.write(handle, data, withResponse)

    def _enableNotification(self, handle, value=True):
        self.peer.enableNotification(handle, value)

    def _handleNotification(self, handle, data):
        if handle == Handles.MOTION:
            d = decodeMotion(data)
        elif handle == Handles.BUTTON:
            d = decodeButton(data)
        elif handle == Handles.TOIO_ID:
            d = decodeToioID(data)
        else:
            d = data

        for listener in self.listeners[handle]:
            listener(d)

    def release(self):
        self.peer.disconnect()

    def addListener(self, handle, listener):
        self.listeners[handle].append(listener)

    def getConfigProtocolVersion(self):
        self._write(Handles.CONFIG, encodeConfigProtocolVersionRequest(), True)
        sleep(0.1)
        return decodeConfigProtocolVersionResponse(self._read(Handles.CONFIG))

    def setMotor(self, left, right, duration=0):
        self._write(Handles.MOTOR, encodeMotor(int(left), int(right), duration))

    def setLight(self, r, g, b, duration=0):
        self._write(Handles.LIGHT, encodeLight(r, g, b, duration))

    def setLightPattern(self, lights, repeat=0):
        self._write(Handles.LIGHT, encodeLightPattern(lights, repeat))

    def setSoundEffect(self, id, volume=255):
        self._write(Handles.SOUND, encodeSound(id, volume))

    def setMusic(self, notes, repeat=0):
        self._write(Handles.SOUND, encodeSoundByNotes(notes, repeat))
    
    def setConfigCollisionThreshold(self, value):
        self._write(Handles.CONFIG, encodeConfigCollisionThreshold(value))

    def setConfigCollisionThreshold(self, angle):
        self._write(Handles.CONFIG, encodeConfigLevelThreshold(angle))


class Cubes(list):
    def __init__(self, cubes):
        super().__init__(cubes)

    def release(self):
        for c in self:
            c.release()
