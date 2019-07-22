import logging as log
from enum import Enum
from random import random
from time import sleep, time
from typing import cast

from tomotoio.data import Motion, Note, PositionID
from tomotoio.geo import Vector
from tomotoio.navigator import NavigationCommandBase, RotateCommand
from utils import createCubes, createNavigators, releaseCubes

BALL_KICKED_SOUND = [Note(90, 0.05), Note(87, 0.05), Note(84, 0.05)]
BALL_STOP_SOUND = [Note(83, 0.05)]
PLAYER_MOVE_SOUND = [
    [Note(70, 0.05), Note(73, 0.05), Note(Note.REST, 0.4)],
    [Note(68, 0.05), Note(71, 0.05), Note(Note.REST, 0.4)]
]
PLAYER_BACK_SOUND = [Note(76, 0.05), Note(82, 0.05)]


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
                    if dt > 0.2:
                        k = v.magnitude() / dt
                        if k > 7 and time() - self.releaseTime > 0.2:
                            self.positionBeforeKicked = None
                            self.vector = v * (10 + 2 / dt)
                            self.rotateCommand = RotateCommand(self.nav, v.direction(), 10)
                            self.state = self.State.ROTATE
                            self.nav.cube.setMusic(BALL_KICKED_SOUND, 1)
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
                self.nav.cube.setMusic(BALL_STOP_SOUND, 1)
                log.debug("BALL: trans to STANDBY")


cubes = createCubes()
navs = createNavigators(cubes)
(player, ball) = (navs[0], navs[1])

ball.setCommand(BallCommand(ball))

try:
    playerTrace = list()
    moveSound = 0
    while True:
        sleep(0.1)
        if ball.lastPosition and player.lastPosition:
            bp = Vector(ball.lastPosition)
            pp = Vector(player.lastPosition)
            bpp = pp - bp
            if cast(BallCommand, ball.command).state == BallCommand.State.STANDBY:
                cbp = bp - ball.mat.center
                m = ball.mat.margin(bp.x, bp.y)
                a = abs(bpp.angle(cbp))
                if m < 100 and a > 45:
                    player.circle(bp.x, bp.y, 30)
                else:
                    player.move(bp.x, bp.y, 20, fixedSpeed=True, moveRotateThreshold=30)
                    player.cube.setMusic(PLAYER_MOVE_SOUND[moveSound], 0)
                    moveSound = (moveSound + 1) % len(PLAYER_MOVE_SOUND)

                    playerTrace.append(bp)
                    if len(playerTrace) > 20:
                        playerTrace = playerTrace[-20:]
                        dx = max([p.x for p in playerTrace]) - min([p.x for p in playerTrace])
                        dy = max([p.y for p in playerTrace]) - min([p.y for p in playerTrace])
                        if dx < 5 and dy < 5:
                            player.setCommand(None)
                            player.cube.setMotor(-60, -60, 0.2)
                            player.cube.setMusic(PLAYER_BACK_SOUND, 5)
                            sleep(0.2)
                            playerTrace = list()

            else:
                if player.command and bpp.magnitude() < 40:
                    player.setCommand(None)
                    player.cube.setMotor(-60, -60, 0.2)
                    sleep(0.2)

finally:
    # Disconnect
    releaseCubes(cubes)
