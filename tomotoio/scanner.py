import argparse
import logging as log
import sys

from bluepy.btle import UUID, DefaultDelegate, Scanner

from tomotoio.constants import UUIDs


class DebugScanDelegate(DefaultDelegate):
    def __init__(self):
        super().__init__()

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            message = "Discovered device"
        elif isNewData:
            message = "Received new data from"
        else:
            return

        log.debug("%s %s (RSSI=%ddB)" % (message, dev.addr, dev.rssi))
        for (adtype, desc, value) in dev.getScanData():
            log.debug("  %s (%d): %s" % (desc, adtype, value))


def scanCubes(timeout, iface=0):
    result = list()
    scanner = Scanner(iface).withDelegate(DebugScanDelegate())
    devices = scanner.scan(timeout)
    for dev in devices:
        for (adtype, desc, value) in dev.getScanData():
            if adtype == 0x07 and UUID(value) == UUIDs.SERVICE:
                result.append(dev.addr)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='iface', type=int,
                        help="Bluetooth interface number", default=0)
    parser.add_argument('-t', dest='timeout', type=int,
                        help="Timeout in seconds", default=10)
    parser.add_argument('-v', dest='verbose',
                        action='store_true', help="Verbose logging")

    try:
        args = parser.parse_args()
    except:
        sys.exit(1)

    log.basicConfig(level=log.DEBUG)
    log.info("Scanning the cubes for %d seconds..." % args.timeout)
    cubes = scanCubes(args.timeout, args.iface)
    for cube in sorted(cubes):
        print(cube)
