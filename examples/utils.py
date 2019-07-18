import logging as log
from time import sleep

from tomotoio.data import Light, Note
from tomotoio.factory import createCubesFromFile
from tomotoio.navigator import Navigator


def createCubes(logLevel=log.DEBUG, cubesFile="toio-cubes.txt", initialReport=True, iface=0):
    log.basicConfig(level=logLevel)

    cubes = createCubesFromFile(cubesFile, iface=iface)

    sleep(0.5)

    if initialReport:
        runInitialReport(cubes)

    return cubes


def runInitialReport(cubes):
    onDuration = 0.2
    offDuration = 0.1
    repeat = 3
    colors = [
        Light(255, 0, 0, onDuration),
        Light(0, 255, 0, onDuration),
        Light(0, 255, 255, onDuration),
        Light(255, 0, 255, onDuration),
    ]

    for i, c in enumerate(cubes):
        log.info("Cube %d: Battery=%d", i + 1, c.battery.get())
        c.setLightPattern([colors[i % len(colors)], Light(0, 0, 0, offDuration)], repeat)
        c.setMusic([Note(80, 0.1), Note(Note.REST, 0.05)], i + 1)
        sleep(1)


def createNavigators(cubes):
    return [Navigator(c) for c in cubes]
