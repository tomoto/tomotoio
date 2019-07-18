from time import sleep

from tomotoio.geo import Vector
from utils import createNavigators, createCubes

cubes = createCubes()
navs = createNavigators(cubes)

(chaser, target) = (navs[0], navs[1])

isComplete = False

try:
    while True:
        sleep(0.1)

        (cp, tp) = (chaser.lastPosition, target.lastPosition)
        if cp and tp:
            chaser.rotate(Vector(cp, tp).direction(), 5)

        if chaser.command and chaser.command.complete != isComplete:
            isComplete = chaser.command.complete
            chaser.cube.setSoundEffect(6 if isComplete else 3)

finally:
    cubes.release()
