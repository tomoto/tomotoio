import logging as log
from functools import partial
from time import sleep

from tomotoio.cube import Cube
from utils import createCubes, releaseCubes

# Identify each cube by the color and the sound signal,
# and report the battery level on the console.
cubes = createCubes()

try:
    for i, c in enumerate(cubes):
        print("Cube #%d" % (i + 1))
        print("Level threshold [1-45 degrees]: ", end='')
        c.setConfigLevelThreshold(int(input() or 45))
        print("Collision threshold [1-10]: ", end='')
        c.setConfigCollisionThreshold(int(input() or 7))
        print("Double tap timing threshold [0-7]: ", end='')
        c.setConfigDoubleTapTiming(int(input() or 5))

    def listener(cube: Cube, e):
        log.debug("%s, %s", cube.name, e)

    for cube in cubes:
        cube.motion.addListener(partial(listener, cube))
        cube.motion.enableNotification()

    while True:
        sleep(1)

finally:
    # Disconnect
    releaseCubes(cubes)
