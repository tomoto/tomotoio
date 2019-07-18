import logging as log
from time import sleep

from utils import createCubes

# Identify each cube by the color and the sound signal,
# and report the battery level on the console.
cubes = createCubes()

try:
    for i in range(0, 11):
        log.info("Sound #%d", i)
        for cube in cubes:
            cube.setSoundEffect(i)
            sleep(0.05)
        sleep(1)

finally:
    # Disconnect
    cubes.release()
