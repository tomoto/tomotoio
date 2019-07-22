import logging as log
from datetime import datetime
from functools import partial
from time import sleep

from utils import createCubes, releaseCubes, Cube

cubes = createCubes()

try:
    def listener(cube: Cube, notificationType: str, e):
        log.debug("%s, %s, %s, %s", datetime.now().isoformat(), cube.name, notificationType, e)

    for cube in cubes:
        cube.button.addListener(partial(listener, cube, 'button'))
        cube.button.enableNotification()
        cube.motion.addListener(partial(listener, cube, 'motion'))
        cube.motion.enableNotification()
        cube.toioID.addListener(partial(listener, cube, 'toioID'))
        cube.toioID.enableNotification()

    while True:
        sleep(1)

finally:
    releaseCubes(cubes)
