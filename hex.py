# NOTE: Pygame has the origin of (x, y) = (0, 0) in the top-left corner, with
#  x increasing from left to right, and y increasing from up to down.
#  Thus, the northern-most vertex of a hexagon drawn in this manner will have
#  a y-value less than the center of the hexagon.
import numpy
import random
import time
random.seed(time.time())


def RANDOM_COLOR():
  return [random.randint(0, 255) for i in range(3)]


class Hexagon:
  def __init__(self, center, northern_most_unit_vector_direction, side_length):
    # The Hexagon class is a representation of a 2D planar hexagon,
    #  represented in Cartesian coordinates of the center and all vertices.
    #
    # center := an absolute point representing the center of hexagon in a
    #  Cartesian coordinate system.
    #
    # northern_most_vertex_direction := a free unit vector indicating the
    #  direction of the northern-most vertex.
    #
    # side_length := a scalar representing the length of any side of the
    #  resulting hexagon.
    self.center = numpy.array([center]).T
    north_dir = side_length*numpy.array([northern_most_unit_vector_direction]).T
    north = north_dir + self.center

    # From the center point and the north vertex, we can compute the other
    #  vertices of the hexagon. Each vertex, relative to the center, is
    #  simply the previous vector rotated by 60 degrees (pi/3 radians).
    pi_d_3 = numpy.pi/3
    sin_60_degrees = numpy.sin(pi_d_3)
    cos_60_degrees = numpy.cos(pi_d_3)
    rotate = numpy.matrix([
      [cos_60_degrees, -sin_60_degrees],
      [sin_60_degrees, cos_60_degrees],
    ])

    # Perform this rotation five times to calculate the direction of all
    #  six hexagon vertices.
    self.vertex_directions = [north_dir]
    self.vertices = [north]
    for i in range(5):
      prev_direction = self.vertex_directions[-1]
      rotated_direction = rotate * prev_direction
      self.vertex_directions.append(rotated_direction)

      # Calculate Cartesian coordinates of vertex.
      vertex = rotated_direction + self.center
      self.vertices.append(vertex)


  def draw(self, screen, color=RANDOM_COLOR()):
    from pprint import pprint
    pygame.draw.polygon(screen, color, self.vertices)


  def draw_vertices(self, screen, color=RANDOM_COLOR()):
    for p in self.vertices:
      pygame.draw.circle(screen, color, p, 4)


if __name__ == "__main__":
  # Pygame requires integers for drawing coordinates, not real values.
  #  Hexagons have a lot of sqrt(3) in their calculations since they are
  #  composed of six equilateral triangles (or twelve 30-60-90 triangles).
  #  Since the length of one edge a is 1 and the length of the other edge
  #  b is sqrt(3), I had to find an integer coefficient x such that
  #  x*sqrt(3) is approximately an integer with minimal loss of accuracy
  #  when rounding. Having x = 26 is sufficient, as 26*sqrt(3) ~= 45.
  #  Thus, the equilateral triangles that make up a hexagon will have
  #  the length of side a equal to 26, and the length of side b equal to 45.
  #  This results in the hexagon composed of these triangles having a side
  #  length of 45.
  import pygame
  import sys
  MAX_X = 640
  MAX_Y = 480

  pygame.init()
  screen = pygame.display.set_mode((MAX_X, MAX_Y))
  h = Hexagon(
    center=(MAX_X/2, MAX_Y/2),
    northern_most_unit_vector_direction=(0, 1),
    side_length=100
  )
  h.draw(screen)

  pygame.display.update()
  while True:
    for event in pygame.event.get(): 
      if event.type == pygame.QUIT: 
        sys.exit(0) 
      else:
        print(event)

