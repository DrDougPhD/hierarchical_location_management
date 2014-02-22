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
    self.side_length = side_length
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
    self.northeast_hexagon = None
    self.east_hexagon = None
    self.southeast_hexagon = None
    self.southwest_hexagon = None
    self.west_hexagon = None
    self.northwest_hexagon = None
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


  def create_northeast_hexagon(self):
    center = self.center + self.northeast_dir + self.north_dir
    hexagon = Hexagon(
      center=center,
      northern_most_unit_vector_direction=self.north_unit_dir,
      side_length=self.side_length
    )
    self.northeast_hexagon = hexagon
    hexagon.southwest_hexagon = self
    return hexagon


  def create_east_hexagon(self):
    center = self.center + self.northeast_dir + self.southeast_dir
    hexagon = Hexagon(
      center=center,
      northern_most_unit_vector_direction=self.north_unit_dir,
      side_length=self.side_length
    )
    self.east_hexagon = hexagon
    hexagon.west_hexagon = self
    return hexagon


  def create_southeast_hexagon(self):
    center = self.center + self.southeast_dir + self.south_dir
    hexagon = Hexagon(
      center=center,
      northern_most_unit_vector_direction=self.north_unit_dir,
      side_length=self.side_length
    )
    self.southeast_hexagon = hexagon
    hexagon.northwest_hexagon = self
    return hexagon


  def create_southwest_hexagon(self):
    center = self.center + self.south_dir + self.southwest_dir
    hexagon = Hexagon(
      center=center,
      northern_most_unit_vector_direction=self.north_unit_dir,
      side_length=self.side_length
    )
    self.southwest_hexagon = hexagon
    hexagon.northeast_hexagon = self
    return hexagon


  def create_west_hexagon(self):
    center = self.center + self.southwest_dir + self.northwest_dir
    hexagon = Hexagon(
      center=center,
      northern_most_unit_vector_direction=self.north_unit_dir,
      side_length=self.side_length
    )
    self.west_hexagon = hexagon
    hexagon.east_hexagon = self
    return hexagon


  def create_northwest_hexagon(self):
    center = self.center + self.northwest_dir + self.north_dir
    hexagon = Hexagon(
      center=center,
      northern_most_unit_vector_direction=self.north_unit_dir,
      side_length=self.side_length
    )
    self.northwest_hexagon = hexagon
    hexagon.southeast_hexagon = self
    return hexagon


def recursive_draw_hexagons(hexagon, max_x, max_y, side_length, screen):
  # Create all hexagons adjacent to the one passed in, and link them together
  #  relative to their topological relationship.
  no_NE = hexagon.northeast_hexagon is None
  no_E = hexagon.east_hexagon is None
  no_SE = hexagon.southeast_hexagon is None
  no_SW = hexagon.southwest_hexagon is None
  no_W = hexagon.west_hexagon is None
  no_NW = hexagon.northwest_hexagon is None

  if no_NE:
    ne_hexagon = hexagon.create_northeast_hexagon()
    ne_hexagon.draw(screen)

  if no_E:
    e_hexagon = hexagon.create_east_hexagon()
    e_hexagon.draw(screen)

  if no_SE:
    we_hexagon = hexagon.create_southeast_hexagon()
    se_hexagon.draw(screen)

  if no_SW:
    sw_hexagon = hexagon.create_southwest_hexagon()
    sw_hexagon.draw(screen)

  if no_W:
    w_hexagon = hexagon.create_west_hexagon()
    w_hexagon.draw(screen)

  if no_NW:
    nw_hexagon = hexagon.create_northwest_hexagon()
    nw_hexagon.draw(screen)

  # After all of the above is executed, all neighbor hexagon pointers of the
  #  current hexagon are not None.
  ne_hexagon.southeast_hexagon = e_hexagon
  e_hexagon.northwest_hexagon = ne_hexagon

  # Connect east hexagon to the southeast hexagon.
  e_hexagon.southwest_hexagon = se_hexagon
  se_hexagon.northeast_hexagon = e_hexagon

  # Connect southeast hexagon to the southwest hexagon.
  se_hexagon.west_hexagon = sw_hexagon
  sw_hexagon.east_hexagon = se_hexagon

  # Connect southwest hexagon to the west hexagon.
  sw_hexagon.northwest_hexagon = w_hexagon
  w_hexagon.southeast_hexagon = sw_hexagon

  # Connect west hexagon to the northwest hexagon.
  w_hexagon.northeast_hexagon = nw_hexagon
  nw_hexagon.southwest_hexagon = w_hexagon

  # Connect northwest hexagon to the north hexagon.
  nw_hexagon.west_hexagon = ne_hexagon
  ne_hexagon.east_hexagon = nw_hexagon


def draw_all_hexagons(max_x, max_y, side_length, screen):
  initial_hex = Hexagon(
    center=numpy.array([(max_x/2, max_y/2)]).T,
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

