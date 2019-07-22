"""Toio as a mouse

Move - move
Tap - click
Rotate - scroll

Note:
- Install pyuserinput (pip install pyuserinput) before running.
- Be careful, it may move when you don't want!
"""
import logging as log
from functools import partial
from random import randint, random
from time import sleep, time
from typing import Optional

from pymouse import PyMouse

from tomotoio.data import Motion, PositionID
from tomotoio.geo import angleDiff
from utils import Cube, createCubes, releaseCubes

mouse = PyMouse()

cubes = createCubes()
cube = cubes[0]
lastPosition: Optional[PositionID] = None
lastTime = time()

try:
    def positionListener(e):
        global lastPosition, lastTime
        if isinstance(e, PositionID):
            if time() - lastTime > 0.05: # throttling
                lastTime = time()
                
                if lastPosition:
                    p = mouse.position()
                    (dx, dy) = (e.x - lastPosition.x, e.y - lastPosition.y)
                    mouse.move(p[0] + dx * 10, p[1] + dy * 10)
                    
                    k0 = lastPosition.angle // 5
                    k1 = e.angle // 5
                    k = (k1 - k0 + 36) % 72 - 36
                    
                    if abs(k) >= 2:
                        mouse.scroll(vertical=-k)
                    
                lastPosition = e
        else:
            lastPosition = None

    def clickListener(e: Motion):
        if (e.collision):
            p = mouse.position()
            mouse.click(*p)
            cube.setSoundEffect(1)
            cube.setMotor(100, 100, 0.2)

    cube.toioID.addListener(positionListener)
    cube.toioID.enableNotification()
    cube.motion.addListener(clickListener)
    cube.motion.enableNotification()

    while True:
        sleep(10)
        cube.setSoundEffect(2)
        rt = 0.2 + random()
        cube.setMotor(100, -100, rt)
        sleep(rt)
        cube.setMotor(100, 100, 0.2)

finally:
    # Disconnect
    releaseCubes(cubes)
