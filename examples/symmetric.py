from time import sleep

from tomotoio.navigator import Mat
from utils import createCubes, createNavigators, releaseCubes

cubes = createCubes()
navs = createNavigators(cubes)

(chaser, target) = (navs[0], navs[1])

isComplete = False

try:
    while True:
        sleep(0.1)

        tp = target.lastPosition
        if tp:
            p = target.mat.center * 2 - tp
            chaser.move(p.x, p.y, 10)

        if chaser.command and chaser.command.complete != isComplete:
            isComplete = chaser.command.complete
            chaser.cube.setSoundEffect(6 if isComplete else 3)

finally:
    releaseCubes(cubes)
