import logging as log
from functools import partial
from time import sleep

from tomotoio.geo import Vector
from utils import createCubes, createNavigators, releaseCubes

cubes = createCubes()
navs = createNavigators(cubes)

for i in range(2):
    def handleCollision(k, e):
        if e.collision:
            cubes[k].setSoundEffect(6 + k)

    cubes[i].motion.enableNotification()
    cubes[i].motion.addListener(partial(handleCollision, i))

try:
    while True:
        sleep(0.1)
        if all([nav.lastPosition for nav in navs]):
            break

    m = [1500, 500]
    m0 = 500
    v = [Vector(0, 0) for nav in navs]

    while True:
        sleep(0.1)

        p = [Vector(nav.lastPosition) for nav in navs]

        for i in range(2):
            j = 1 - i

            d = Vector(p[i], p[j])
            l = d.magnitude()
            if l != 0:
                v[i] += d.normalize() * (1 / l - 2000 / l ** 3) * m[j]

            d = Vector(p[i], navs[i].mat.center)
            l = d.magnitude()
            if l != 0:
                v[i] += d.normalize() * (1 / l) * m0

            q = p[i] + v[i]
            if q.x - navs[i].mat.topLeft.x < 20 or navs[i].mat.bottomRight.x - q.x < 20:
                v[i].x = 0
            if q.y - navs[i].mat.topLeft.y < 20 or navs[i].mat.bottomRight.y - q.y < 20:
                v[i].y = 0

            navs[i].move(q.x, q.y, 0, moveRotateThreshold=60)

finally:
    releaseCubes(cubes)
