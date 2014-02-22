# NOTE: Pygame has the origin of (x, y) = (0, 0) in the top-left corner, with
#  x increasing from left to right, and y increasing from up to down.
#  Thus, the northern-most vertex of a hexagon drawn in this manner will have
#  a y-value less than the center of the hexagon.
import numpy
import random
import time
random.seed(time.time())

MAX_X = 640
MAX_Y = 480

def RANDOM_COLOR():
  return [random.randint(0, 255) for i in range(3)]


def is_column_vector(v):
  # v := a numpy array
  return 1 == v.shape[1]


class Hexagon:
  def __init__(self, center, northern_most_unit_vector_direction, side_length):
    # The Hexagon class is a representation of a 2D planar hexagon,
    #  represented in Cartesian coordinates of the center and all vertices.
    #
    # center := an absolute point, as a 2D numpy column vector, representing
    #  the center of hexagon in a Cartesian coordinate system.
    #
    # northern_most_vertex_direction := a free unit vector, as a 2D numpy
    #  column vector, indicating the direction of the northern-most vertex.
    #
    # side_length := a scalar representing the length of any side of the
    #  resulting hexagon.
    self.center = center.copy()
    self.north_unit_dir = northern_most_unit_vector_direction.copy()
    scaled_north_dir = side_length * northern_most_unit_vector_direction
    north = scaled_north_dir + self.center

    # From the center point and the north vertex, we can compute the other
    #  vertices of the hexagon. Each vertex, relative to the center, is
    #  simply the previous vector rotated by 60 degrees (pi/3 radians).
    pi_d_3 = numpy.pi/3
    sin_60_degrees = numpy.sin(pi_d_3)
    cos_60_degrees = numpy.cos(pi_d_3)
    rotate = numpy.matrix([
      [cos_60_degrees, sin_60_degrees],
      [-sin_60_degrees, cos_60_degrees],
    ])

    # Perform this rotation five times to calculate the direction of all
    #  six hexagon vertices.
    self.vertex_directions = [scaled_north_dir]
    self.vertices = [north]
    for i in range(5):
      prev_direction = self.vertex_directions[-1]
      rotated_direction = rotate * prev_direction
      self.vertex_directions.append(rotated_direction)

      # Calculate Cartesian coordinates of vertex.
      vertex = rotated_direction + self.center
      self.vertices.append(vertex)

    self.north_dir,\
    self.northeast_dir,\
    self.southeast_dir,\
    self.south_dir,\
    self.southwest_dir,\
    self.northwest_dir = self.vertex_directions

    self.north_vertex,\
    self.northeast_vertex,\
    self.southeast_vertex,\
    self.south_vertex,\
    self.southwest_vertex,\
    self.northwest_vertex = self.vertices

    # The following member variables correspond to points to neighboring
    #  hexagons related to the topological relationship between this hexagon
    #  and neighboring hexagons.
    self.to_northeast = None
    self.to_east = None
    self.to_southeast = None
    self.to_southwest = None
    self.to_west = None
    self.to_northwest = None
    self.neighboring_hexagons = []


  def draw(self, screen, color=None):
    if color is None:
      color = RANDOM_COLOR()
    pygame.draw.polygon(
      screen,
      color,
      self.transform_points_for_pygame(self.vertices)
    )


  def draw_vertices(self, screen, color=None):
    if color is None:
      color = RANDOM_COLOR()

    map(
      lambda p: pygame.draw.circle(screen, color, p, 4),
      self.transform_points_for_pygame(self.vertices)
    )


  def transform_points_for_pygame(self, points):
    return [(p[0], MAX_Y - p[1]) for p in points]


def recursive_draw_hexagons(hexagon, max_x, max_y, side_length, screen):
  # Create all hexagons adjacent to the one passed in, and link them together
  #  relative to their topological relationship.
  if hexagon.to_northeast is None:
    ne_center = hexagon.northeast_dir + hexagon.north_dir
    ne_hexagon = Hexagon(
      center=ne_center,
      northern_most_unit_vector_direction=hexagon.north_unit_dir,
      side_length=side_length
    )
    ne_hexagon.draw(screen)

  if hexagon.to_east is None:
    pass

  if hexagon.to_southeast is None:
    pass

  if hexagon.to_southwest is None:
    pass

  if hexagon.to_west is None:
    pass

  if hexagon.to_northwest is None:
    pass


def draw_all_hexagons(max_x, max_y, side_length, screen):
  initial_hex = Hexagon(
    center=numpy.array([(0, 0)]).T,
    northern_most_unit_vector_direction=numpy.array([(0, 1)]).T,
    side_length=100
  )
  initial_hex.draw(screen)

  recursive_draw_hexagons(initial_hex, max_x, max_y, side_length, screen)


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

  pygame.init()
  screen = pygame.display.set_mode((MAX_X, MAX_Y))
  draw_all_hexagons(
    max_x=MAX_X,
    max_y=MAX_Y,
    side_length=100,
    screen=screen
  )

  pygame.display.update()
  while True:
    for event in pygame.event.get(): 
      if event.type == pygame.QUIT: 
        sys.exit(0) 
      else:
        print(event)

