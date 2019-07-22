import logging as log
from math import hypot
from time import sleep

from tomotoio.geo import Vector
from utils import createCubes, createNavigators, releaseCubes

cubes = createCubes()
navs = createNavigators(cubes)

(chaser, target) = (navs[0], navs[1])

center = None

try:
    while True:
        sleep(0.1)

        (cp, tp) = (chaser.lastPosition, target.lastPosition)
        if cp and tp:
            if center is None or Vector(center, tp).magnitude() > 10:
                center = tp
                chaser.circle(tp.x, tp.y, Vector(tp, cp).magnitude())
                chaser.cube.setSoundEffect(3)

finally:
    releaseCubes(cubes)
