import sys

from .blepeer import BlePeer
from .cube import Cube, Cubes


def createCube(address, iface=0):
    return Cube(BlePeer(address, iface))


def createCubesFromFile(addressesFile=None, iface=0):
    def readAddresses(f):
        return [s.strip() for s in f.readlines()]

    if addressesFile:
        with open(addressesFile) as f:
            addresses = readAddresses(f)
    else:
        addresses = readAddresses(sys.stdin)

    return Cubes([createCube(a, iface) for a in addresses])
