import logging as log
from queue import Empty, Queue
from threading import Thread, currentThread
from typing import Any, Callable, List, Optional, Mapping

from bluepy.btle import (ADDR_TYPE_RANDOM, BTLEInternalError, DefaultDelegate,
                         Peripheral, UUID)

from .cube import Peer, PeerListenerFunc


class BlePeer(Peer, DefaultDelegate):
    def __init__(self, address: str, iface: int = 0):
        super().__init__()
        self.peripheral: Peripheral = Peripheral(address, ADDR_TYPE_RANDOM, iface).withDelegate(self)
        self.listeners: List[PeerListenerFunc] = list()
        self.notificationThread: Optional[Thread] = None
        self.writeQueue: Queue = Queue(100)
        self.uuidHandleMap: Mapping[UUID, int] = dict()
        self.handleUUIDMap: Mapping[int, UUID] = dict()
        
        for c in self.peripheral.getCharacteristics():
            self.uuidHandleMap[c.uuid] = c.getHandle()
            self.handleUUIDMap[c.getHandle()] = c.uuid

    def disconnect(self):
        self.peripheral.disconnect()

    def _read(self, handle: int) -> bytes:
        return self.peripheral.readCharacteristic(handle)
    
    def _write(self, handle: int, data: bytes, withResponse: bool = False):
        if self.notificationThread and self.notificationThread != currentThread():
            self.writeQueue.put((handle, data, withResponse))
        else:
            self.peripheral.writeCharacteristic(handle, data, withResponse)
    
    def _enableNotification(self, handle: int, value: bool = True):
        if value and not self.notificationThread:
            self._startNotificationThread()

        self._write(handle+1, bytes([int(value), 0]))
        
    def read(self, uuid: UUID) -> bytes:
        return self._read(self.uuidHandleMap[uuid])

    def write(self, uuid: UUID, data: bytes, withResponse: bool = False):
        self._write(self.uuidHandleMap[uuid], data, withResponse)

    def enableNotification(self, uuid: UUID, value: bool = True):
        self._enableNotification(self.uuidHandleMap[uuid], value)

    def addListener(self, listener: PeerListenerFunc):
        self.listeners.append(listener)

    def handleNotification(self, handle: int, data: bytes):
        for listener in self.listeners:
            listener(self.handleUUIDMap[handle], data)

    def _startNotificationThread(self):
        t = Thread(name="Notification for %s" % self, target=self._processNotifications)
        t.setDaemon(True)
        self.notificationThread = t
        t.start()

    def _processNotifications(self):
        while True:
            try:
                while True:
                    writeArgs = self.writeQueue.get(False)
                    self._write(*writeArgs)
            except Empty:
                pass

            try:
                self.peripheral.waitForNotifications(0.01)
            except BTLEInternalError as ex:
                log.warn(ex)
