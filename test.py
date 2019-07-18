import time
import logging

import toio.data as td
from toio.factory import createCubesFromFile


logging.basicConfig(level=logging.DEBUG)


def log(s):
    logging.info(s)


cubes = createCubesFromFile("toio-cubes.txt")


time.sleep(1)


for cube in cubes:
    log(cube.battery.get())
    log(cube.getConfigProtocolVersion())
    cube.motion.enableNotification()
    cube.button.enableNotification()
    cube.toioID.enableNotification()
    cube.setListener(log)

cube.setSoundByNotes([td.Note(0x3c, 0.3), td.Note(0x3e, 0.3), td.Note(0x40, 0.3)])
cube.setLight(0, 0, 255)
cube.setLightPattern([td.Light(255, 0, 0, 0.5), td.Light(0, 255, 0, 0.5)])
cube.setMotor(30, 10)

while True:
    if not cube.peer.peripheral.waitForNotifications(5):
        break

for c in cubes:
    c.release()
    