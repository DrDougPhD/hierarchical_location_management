# NOTE: Pygame has the origin of (x, y) = (0, 0) in the top-left corner, with
#  x increasing from left to right, and y increasing from up to down.
#  Thus, the northern-most vertex of a hexagon drawn in this manner will have
#  a y-value less than the center of the hexagon.
import numpy
import math
import random
import time
random.seed(time.time())

HEXAGONS_ALONG_X_AXIS = 40
HEXAGONS_ALONG_Y_AXIS = 40

def RANDOM_COLOR():
  return [random.randint(0, 255) for i in range(3)]


def is_column_vector(v):
  # v := a numpy array
  return 1 == v.shape[1]


def is_within_frame(v):
  x, y = v
  return 0 <= x <= MAX_X and 0 <= y <= MAX_Y


class Hexagon:
  number_of_sides = 6
  neighbor_order = ["NE", "E", "SE", "SW", "W", "NW"]
  vertex_order = ["N", "NE", "SE", "S", "SW", "NW"]
  neighbor_index = {"NE": 0, "E": 1, "SE": 2, "SW": 3, "W": 4, "NW": 5}
  vertex_order = {"N": 0, "NE": 1, "SE": 2, "S": 3, "SW": 4, "NW": 5}

  def __init__(self, center=None, northern_most_unit_vector_direction=None, side_length=None, screen=None):
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

    if center is not None and\
       northern_most_unit_vector_direction is not None and\
       side_length is not None:
      self.set(center, northern_most_unit_vector_direction, side_length)
      self.initialized = True
    else:
      self.initialized = False

    self.screen = screen


  def set(self, center, northern_most_unit_vector_direction, side_length):
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
    self.neighboring_hexagons = [None for i in range(6)]
    self.northeast_hexagon,\
    self.east_hexagon,\
    self.southeast_hexagon,\
    self.southwest_hexagon,\
    self.west_hexagon,\
    self.northwest_hexagon = self.neighboring_hexagons


  def draw(self, screen, color=None):
    if self.initialized:
      if color is None:
        color = RANDOM_COLOR()
      pygame.draw.polygon(
        self.screen,
        color,
        self.transform_points_for_pygame(self.vertices)
      )


  def draw_vertices(self, screen, color=None):
    if self.initialized:
      if color is None:
        color = RANDOM_COLOR()
      map(
        lambda p: pygame.draw.circle(self.screen, color, p, 4),
        self.transform_points_for_pygame(self.vertices)
      )


  def transform_points_for_pygame(self, points):
    return [(p[0], MAX_Y - p[1]) for p in points]


  def create_neighbor(self, i):
    # Create the neighbor of this hexagon according to the neighbor index.
    center = self.center + self.vertex_directions[i] +\
             self.vertex_directions[self.next_neighbor_index(i)]
    hexagon = Hexagon(
      center=center,
      northern_most_unit_vector_direction=self.north_unit_dir,
      side_length=self.side_length,
      screen=self.screen
    )

    self.set_neighbor(hexagon, i)
    return hexagon


  def previous_neighbor_index(self, i):
    return (i-1)%self.number_of_sides


  def next_neighbor_index(self, i):
    return (i+1)%self.number_of_sides


  def create_northeast_hexagon(self):
    return self.create_neighbor(0)


  def create_east_hexagon(self):
    return self.create_neighbor(1)


  def create_southeast_hexagon(self):
    return self.create_neighbor(2)


  def create_southwest_hexagon(self):
    return self.create_neighbor(3)


  def create_west_hexagon(self):
    return self.create_neighbor(4)


  def create_northwest_hexagon(self):
    return self.create_neighbor(5)


  def set_neighbor(self, neighbor, direction_index):
    self.neighboring_hexagons[direction_index] = neighbor
    neighbor.neighboring_hexagons[(direction_index+3)%6] = self
    #pygame.draw.line(
    #  self.screen,
    #  (255,255,255),
    #  self.transform_points_for_pygame([self.center])[0],
    #  self.transform_points_for_pygame([neighbor.center])[0]
    #)


  def set_northeast_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 0)


  def set_east_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 1)


  def set_southeast_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 2)


  def set_southwest_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 3)


  def set_west_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 4)


  def set_northwest_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 5)


def draw_all_hexagons(side_length, screen):
  # Create all hexagons within the viewing window.
  previous_hexagon = Hexagon(
    center=numpy.array([(0, 0)]).T,
    northern_most_unit_vector_direction=numpy.array([(0, 1)]).T,
    side_length=side_length,
    screen=screen
  )
  first_hexagon = previous_hexagon
  hexagon_matrix = []
  for y in range(HEXAGONS_ALONG_Y_AXIS):
    hexagon_row = []
    for x in range(HEXAGONS_ALONG_X_AXIS-1):
      previous_hexagon.draw(screen)
      new_hexagon = previous_hexagon.create_east_hexagon()
      hexagon_row.append(previous_hexagon)
      previous_hexagon = new_hexagon

    previous_hexagon.draw(screen)
    hexagon_row.append(previous_hexagon)
    hexagon_matrix.append(hexagon_row)

    if y != HEXAGONS_ALONG_Y_AXIS-1:
      even_row = y % 2 == 0
      if even_row:
        first_hexagon = previous_hexagon = first_hexagon.create_northeast_hexagon()
      else:
        first_hexagon = previous_hexagon = first_hexagon.create_northwest_hexagon()

  # Connect each hexagon together.
  for y in range(HEXAGONS_ALONG_Y_AXIS-1):
    current_row = hexagon_matrix[y]
    above_row = hexagon_matrix[y+1]

    for x in range(HEXAGONS_ALONG_X_AXIS):
      lower_hex = current_row[x]
      upper_hex = above_row[x]
      even_row = y%2 == 0
      if even_row:
        lower_hex.set_northeast_neighbor(upper_hex)
      else:
        lower_hex.set_northwest_neighbor(upper_hex)

    for x in range(HEXAGONS_ALONG_X_AXIS-1):
      if even_row:
        current_row[x+1].set_northwest_neighbor(above_row[x])
      else:
        current_row[x].set_northeast_neighbor(above_row[x+1])

  
  #recursive_draw_eastern_hexagons(initial_hex, screen, "INIT")
  #recursive_draw_western_hexagons(initial_hex, screen, "INIT")


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
  side_length = 10
  
  MAX_X = int(math.ceil(2*numpy.sin(numpy.pi/3)*side_length*(HEXAGONS_ALONG_X_AXIS-1)))
  MAX_Y = int(math.ceil(1.5*side_length*(HEXAGONS_ALONG_Y_AXIS-1)))
  print("Screen size: ({0}, {1})".format(MAX_X, MAX_Y))
  pygame.init()
  screen = pygame.display.set_mode((MAX_X, MAX_Y))
  draw_all_hexagons(
    side_length=side_length,
    screen=screen
  )

  pygame.display.update()
  while True:
    for event in pygame.event.get(): 
      if event.type == pygame.QUIT: 
        sys.exit(0) 
      else:
        print(event)

