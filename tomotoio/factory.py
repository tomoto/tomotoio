import sys
from typing import List

from .blepeer import BlePeer
from .cube import Cube


def createCube(address: str, name: str = None, iface: int = 0) -> Cube:
    return Cube(BlePeer(address, iface), name if name else address)


def createCubesFromFile(addressesFile: str = None, iface: int = 0) -> List[Cube]:
    def readAddresses(f) -> List[str]:
        return [s.strip() for s in f.readlines()]

    if addressesFile:
        with open(addressesFile) as f:
            addresses = readAddresses(f)
    else:
        addresses = readAddresses(sys.stdin)

    return [createCube(a, "Cube #%d" % i, iface) for i, a in enumerate(addresses, 1)]
