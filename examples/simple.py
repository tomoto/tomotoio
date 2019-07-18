import logging as log

from utils import createCubes

# Identify each cube by the color and the sound signal,
# and report the battery level on the console.
cubes = createCubes()

try:
    # do what you want to do
    pass

finally:
    # Disconnect
    cubes.release()
