import sys
import pygame
import constants
import logging
from pygame.locals import *

class simControl():
  """"Controls fundamental Game Loop functions."""
  sim_data_folder = './sim_data/'
  Surface = None
  StopGameLoop = False
  resolution_width = None
  resolution_height = None
  fps_clock = None

  catImg = None
  catx = 100
  caty = 100

  def __init__(self):
    pygame.init()
    self.fps_clock = pygame.time.Clock()
    self.resolution_width = 800
    self.resolution_height = 600


  def PreLoop(self):
    self.Surface = pygame.display.set_mode((800, 600))
    self.catImg = pygame.image.load(self.sim_data_folder+'cat.png')

  def PostLoop(self):
    pygame.quit()

  def _HandleEvents(self):
    for event in pygame.event.get():
      if event.type == QUIT:
        self.StopGameLoop = True


  def _UpdateGameState(self):
    self.catx += 5


  def _DrawScreen(self):
    self.Surface.fill(constants.BLACK)

    self.Surface.blit(self.catImg, (self.catx, self.caty))

  def GameLoop(self):
    self._HandleEvents()
    self._UpdateGameState()
    pygame.display.update()
    self._DrawScreen()



