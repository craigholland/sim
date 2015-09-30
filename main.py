import logging
import sys
import pygame

from code.simcontrol import simControl as SimCon
from code.constants import *

logging.basicConfig(filename='log.txt', level=logging.INFO)

logging.info('SIM STARTED...')

sim = SimCon()
logging.info('SIMCON INITIALIZED...')

sim.PreLoop()
logging.info('PRE-LOOP FINISHED...BEGIN GAME LOOP...')
while not sim.StopGameLoop:
  sim.GameLoop()
  sim.fps_clock.tick(FPS_RATE)
logging.info('GAME LOOP STOPPED...BEGIN CLEAN UP...')
sim.PostLoop()
logging.info('CLEAN UP COMPLETE...EXITING')

sys.exit()