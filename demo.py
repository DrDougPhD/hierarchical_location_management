import sys
#import and init pygame
import pygame
pygame.init()

import random
import time
random.seed(time.time())
from pprint import pprint

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
def RANDOM_COLOR():
  return [random.randint(0, 255) for i in range(3)]


MAX_X = 640
MAX_Y = 480
X_STEP = 26
Y_STEP = 45
import math
SQRT_3 = math.sqrt(3)

#create the screen
screen = pygame.display.set_mode((MAX_X, MAX_Y))

def draw_hex_grid_points(initial_x, initial_y):
  points = []
  y = initial_y
  while y <= MAX_Y:
    x = initial_x
    while x <= MAX_X:
      p = (x, y)
      points.append(p)
      c = pygame.draw.circle(screen, WHITE, p, 1)
      x += 2*X_STEP
    y += 2*Y_STEP

  return points


def draw_hex_centered_at(x, y):
  XdY = X_STEP/SQRT_3
  north = (x, y - (2*XdY))
  south = (x, y + (2*XdY))
  northwest = (x + X_STEP, y - XdY)
  southwest = (x + X_STEP, y + XdY)
  northeast = (x - X_STEP, y - XdY)
  southeast = (x - X_STEP, y + XdY)

  points = [
    north,
    northeast,
    southeast,
    south,
    southwest,
    northwest,
    north
  ]

  pygame.draw.polygon(screen, RANDOM_COLOR(), points, 2)
  return points


points = draw_hex_grid_points(0, 0)
points.extend(draw_hex_grid_points(X_STEP, Y_STEP))

for p in points:
  draw_hex_centered_at(*p)

#pygame.draw.polygon(
#  Surface=screen,
#  color=GREEN,
#  pointlist,
#  width=0
#)

#draw it to the screen
pygame.display.update() 

#input handling (somewhat boilerplate code):
while True:
  for event in pygame.event.get(): 
    if event.type == pygame.QUIT: 
      sys.exit(0) 
    else:
      print event

  # erase the screen
  #screen.fill(white)

  # draw the updated picture

  #updatePoints(points)  # changes the location of the points
  #pygame.draw.lines(screen, black, false, points, 1) # redraw the points

  # update the screen
  #pygame.display.update()
