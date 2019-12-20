import logging as log
from time import sleep

from utils import createCubes, releaseCubes

# Identify each cube by the color and the sound signal,
# and report the battery level on the console.
cubes = createCubes(initialReport=True)

try:
    for k in range(10):
        for i, c in enumerate(cubes):
            log.info("Cube #%d, Iteration #%d" % (i, k))
            log.info(c.getConfigProtocolVersion())
            log.info(c.toioID.get())
            log.info(c.motion.get())
            log.info(c.button.get())
            log.info(c.battery.get())
        sleep(0.5)
        
finally:
    # Disconnect
    releaseCubes(cubes)
