import logging as log
from queue import Empty, Queue
from threading import Thread, currentThread

from bluepy.btle import (ADDR_TYPE_RANDOM, BTLEInternalError, DefaultDelegate,
                         Peripheral)


class BlePeer(DefaultDelegate):
    def __init__(self, address, iface=0):
        super().__init__()
        self.peripheral = Peripheral(address, ADDR_TYPE_RANDOM, iface).withDelegate(self)
        self.listeners = []
        self.enabledNotifications = set()
        self.notificationThread = None
        self.writeQueue = Queue(100)

    def disconnect(self):
        self.peripheral.disconnect()

    def read(self, handle):
        return self.peripheral.readCharacteristic(handle)

    def write(self, handle, data, withResponse=False):
        if self.notificationThread and self.notificationThread != currentThread():
            self.writeQueue.put((handle, data, withResponse))
        else:
            self.peripheral.writeCharacteristic(handle, data, withResponse)

    def enableNotification(self, handle, value=True):
        if value:
            self.enabledNotifications.add(handle)
            if not self.notificationThread:
                self._startNotificationThread()
        else:
            self.enabledNotifications.remove(handle)

        self.write(handle+1, bytes([int(value), 0]))

    def addListener(self, listener):
        self.listeners.append(listener)

    def handleNotification(self, handle, data):
        for listener in self.listeners:
            listener(handle, data)

    def _startNotificationThread(self):
        t = Thread(name="Notification for %s" % self, target=self._processNotifications)
        t.setDaemon(True)
        self.notificationThread = t
        t.start()

    def _processNotifications(self):
        while True:
            try:
                while True:
                    w = self.writeQueue.get(False)
                    self.write(*w)
            except Empty:
                pass

            try:
                self.peripheral.waitForNotifications(0.01)
            except BTLEInternalError as ex:
                log.warn(ex)
