import logging as log
from enum import Enum
from random import random
from time import sleep, time

from tomotoio.data import Motion, PositionID
from tomotoio.geo import Vector, angleDiff, direction
from tomotoio.navigator import NavigationCommandBase, RotateCommand
from utils import createCubes, createNavigators


class BallCommand(NavigationCommandBase):
    class State(Enum):
        STANDBY = 1
        ROTATE = 2
        MOVE = 3

    def __init__(self, nav):
        super().__init__(nav)
        self.state = self.State.STANDBY
        self.positionBeforeKicked = None
        self.releaseTime = 0

    def handleNotification(self, e):
        if self.state == self.State.STANDBY:
            self.nav.cube.setMotor(0, 0)
            if isinstance(e, PositionID):
                if self.positionBeforeKicked:
                    v = Vector(self.positionBeforeKicked[0], e)
                    dt = time() - self.positionBeforeKicked[1]
                    if dt > 0.1:
                        k = v.magnitude() / dt
                        if k > 7 and time() - self.releaseTime > 0.2:
                            self.positionBeforeKicked = None
                            self.vector = v * (10 + 2 / dt)
                            self.rotateCommand = RotateCommand(self.nav, direction(v.x, v.y), 10)
                            self.state = self.State.ROTATE
                            log.debug("BALL: trans to ROTATE")
                        else:
                            self.positionBeforeKicked = (e, time())
                            self.collisionCount = 0
                else:
                    self.positionBeforeKicked = (e, time())
                    self.collisionCount = 0

        elif self.state == self.State.ROTATE:
            if not self.rotateCommand.complete:
                self.rotateCommand.handleNotification(e)
            else:
                log.debug("BALL: trans to MOVE")
                self.state = self.State.MOVE

        elif self.state == self.State.MOVE:
            s = self.vector.magnitude()
            self.nav.cube.setMotor(min(100, s), min(s, 100))
            self.vector *= 0.9

            if s < 8:
                self.nav.cube.setMotor(0, 0)
                self.state = self.State.STANDBY
                self.releaseTime = time()
                log.debug("BALL: trans to STANDBY")


cubes = createCubes()
navs = createNavigators(cubes)
(player, ball) = navs

ball.setCommand(BallCommand(ball))

try:
    playerTrace = list()
    while True:
        sleep(0.1)
        if ball.lastPosition and player.lastPosition:
            bp = Vector(ball.lastPosition)
            pp = Vector(player.lastPosition)
            bpp = pp - bp
            if ball.command.state == BallCommand.State.STANDBY:
                cbp = bp - ball.mat.center
                m = ball.mat.margin(bp.x, bp.y)
                a = abs(angleDiff(direction(cbp.x, cbp.y) - direction(bpp.x, bpp.y)))
                if m < 100 and a > 45:
                    player.circle(bp.x, bp.y, 30)
                else:
                    player.move(bp.x, bp.y, fixedSpeed=100, moveRotateThreshold=30, tolerance=20)

                    playerTrace.append(bp)
                    if len(playerTrace) > 20:
                        playerTrace = playerTrace[-20:]
                        dx = max([p.x for p in playerTrace]) - min([p.x for p in playerTrace])
                        dy = max([p.y for p in playerTrace]) - min([p.y for p in playerTrace])
                        if dx < 5 and dy < 5:
                            player.setCommand(None)
                            player.cube.setMotor(-50, -50, 0.2)
                            sleep(0.2)
                            playerTrace = list()

            else:
                if player.command and bpp.magnitude() < 40:
                    player.setCommand(None)
                    player.cube.setMotor(-60, -60, 0.2)
                    sleep(0.2)

finally:
    # Disconnect
    cubes.release()
