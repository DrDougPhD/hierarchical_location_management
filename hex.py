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


def is_within_frame(v):
  x, y = v
  return 0 <= x <= MAX_X and 0 <= y <= MAX_Y


class Hexagon:
  number_of_sides = 6
  neighbor_order = ["NE", "E", "SE", "SW", "W", "NW"]
  vertex_order = ["N", "NE", "SE", "S", "SW", "NW"]
  neighbor_index = {"NE": 0, "E": 1, "SE": 2, "SW": 3, "W": 4, "NW": 5}
  vertex_order = {"N": 0, "NE": 1, "SE": 2, "S": 3, "SW": 4, "NW": 5}

  def __init__(self, center=None, northern_most_unit_vector_direction=None, side_length=None):
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
        screen,
        color,
        self.transform_points_for_pygame(self.vertices)
      )


  def draw_vertices(self, screen, color=None):
    if self.initialized:
      if color is None:
        color = RANDOM_COLOR()
      map(
        lambda p: pygame.draw.circle(screen, color, p, 4),
        self.transform_points_for_pygame(self.vertices)
      )


  def transform_points_for_pygame(self, points):
    return [(p[0], MAX_Y - p[1]) for p in points]


  def create_neighbor(self, i):
    # Create the neighbor of this hexagon according to the neighbor index.
    center = self.center + self.vertex_directions[i] +\
             self.vertex_directions[self.previous_neighbor_index(i)]
    hexagon = Hexagon(
      center=center,
      northern_most_unit_vector_direction=self.north_unit_dir,
      side_length=self.side_length
    )

    self.neighboring_hexagons[i] = hexagon
    hexagon.neighboring_hexagons[(i-3)%self.number_of_sides] = self
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


def draw_hexagon_and_create_neighbors(hexagon, screen, s):
  print("#"*40)
  print(hexagon)
  print(s)

  hexagon.draw(screen)

  # Create all hexagons adjacent to the one passed in, and link them together
  #  relative to their topological relationship.
  no_NE = hexagon.northeast_hexagon is None
  no_E = hexagon.east_hexagon is None
  no_SE = hexagon.southeast_hexagon is None
  no_SW = hexagon.southwest_hexagon is None
  no_W = hexagon.west_hexagon is None
  no_NW = hexagon.northwest_hexagon is None

  if hexagon.northeast_hexagon is None:# no_NE:
    ne_hexagon = hexagon.create_northeast_hexagon()
  else:
    ne_hexagon = hexagon.northeast_hexagon

  if hexagon.east_hexagon is None:# no_E:
    e_hexagon = hexagon.create_east_hexagon()
  else:
    e_hexagon = hexagon.east_hexagon

  if hexagon.southeast_hexagon is None:# no_SE:
    se_hexagon = hexagon.create_southeast_hexagon()
  else:
    se_hexagon = hexagon.southeast_hexagon

  if hexagon.southwest_hexagon is None:# no_SW:
    sw_hexagon = hexagon.create_southwest_hexagon()
  else:
    sw_hexagon = hexagon.southwest_hexagon

  if hexagon.west_hexagon is None:# no_W:
    w_hexagon = hexagon.create_west_hexagon()
  else:
    w_hexagon = hexagon.west_hexagon

  if hexagon.northwest_hexagon is None:# no_NW:
    nw_hexagon = hexagon.create_northwest_hexagon()
  else:
    nw_hexagon = hexagon.northwest_hexagon

  # After all of the above is executed, all neighbor hexagon pointers of the
  #  current hexagon are not None unless the created hexagon's center is out
  #  of bounds.
  NE = not hexagon.northeast_hexagon is None
  E = not hexagon.east_hexagon is None
  SE = not hexagon.southeast_hexagon is None
  SW = not hexagon.southwest_hexagon is None
  W = not hexagon.west_hexagon is None
  NW = not hexagon.northwest_hexagon is None

  if NE and E:
    ne_hexagon.southeast_hexagon = e_hexagon
    e_hexagon.northwest_hexagon = ne_hexagon

  # Connect east hexagon to the southeast hexagon.
  if E and SE:
    e_hexagon.southwest_hexagon = se_hexagon
    se_hexagon.northeast_hexagon = e_hexagon

  # Connect southeast hexagon to the southwest hexagon.
  if SE and SW:
    se_hexagon.west_hexagon = sw_hexagon
    sw_hexagon.east_hexagon = se_hexagon

  # Connect southwest hexagon to the west hexagon.
  if SW and W:
    sw_hexagon.northwest_hexagon = w_hexagon
    w_hexagon.southeast_hexagon = sw_hexagon

  # Connect west hexagon to the northwest hexagon.
  if W and NW:
    w_hexagon.northeast_hexagon = nw_hexagon
    nw_hexagon.southwest_hexagon = w_hexagon

  # Connect northwest hexagon to the north hexagon.
  if NW and NE:
    nw_hexagon.east_hexagon = ne_hexagon
    ne_hexagon.west_hexagon = nw_hexagon


def recursive_draw_eastern_hexagons(hexagon, screen, s):
  if hexagon is None:
    return

  draw_hexagon_and_create_neighbors(hexagon, screen, s)
  if not hexagon.northeast_vertex is None:
    recursive_draw_eastern_hexagons(hexagon.northeast_hexagon, screen, s+"->NE")
  if not hexagon.east_hexagon is None:
    recursive_draw_eastern_hexagons(hexagon.east_hexagon, screen, s+"->E")
  if not hexagon.southeast_hexagon is None:
    recursive_draw_eastern_hexagons(hexagon.southeast_hexagon, screen, s+"->SE")


def recursive_draw_western_hexagons(hexagon, screen, s):
  if hexagon is None:
    return

  draw_hexagon_and_create_neighbors(hexagon, screen, s)
  if not hexagon.southwest_hexagon is None:
    recursive_draw_western_hexagons(hexagon.southwest_hexagon, screen, s+"->SW")
  if not hexagon.west_hexagon is None:
    recursive_draw_western_hexagons(hexagon.west_hexagon, screen, s+"->W")
  if not hexagon.northwest_hexagon is None:
    recursive_draw_western_hexagons(hexagon.northwest_hexagon, screen, s+"->NW")


def recursive_draw_hexagons(hexagon, screen, recursive_index):
  if recursive_index < 5:
    new_hexagons = []
    for i in range(hexagon.number_of_sides):
      hexagons_along_current_side = []
      for j in range(recursive_index):
        neighbor = hexagon.create_neighbor(i)
        neighbor.draw(screen)
        hexagons_along_current_side.append(neighbor)

      new_hexagons.append(hexagons_along_current_side)

    if recursive_index == 1:
      for i in range(hexagon.number_of_sides):
        current_side = new_hexagons[i]
        next_side = new_hexagons[hexagon.next_neighbor_index(i)]

        last_hexagon_of_current_side = new_hexagons[i][-1]
        first_hexagon_of_next_side = new_hexagons[
          hexagon.next_neighbor_index(i)
        ][0]

        last_hexagon_of_current_side.neighboring_hexagons[(i+2)%6] =\
            first_hexagon_of_next_side
        first_hexagon_of_next_side.neighboring_hexagons[
          hexagon.previous_neighbor_index(i)
        ] = last_hexagon_of_current_side

        h1 = hexagon.neighboring_hexagons[i]
        h2 = hexagon.neighboring_hexagons[hexagon.next_neighbor_index(i)]


  #if not hexagon.northeast_vertex is None:
  #  recursive_draw_hexagons(hexagon.northeast_hexagon, screen, s+"->NE")
  #if not hexagon.east_hexagon is None:
  #  recursive_draw_hexagons(hexagon.east_hexagon, screen, s+"->E")
  #if not hexagon.northwest_hexagon is None:
  #  recursive_draw_hexagons(hexagon.northwest_hexagon, screen, s+"->SE")


def draw_all_hexagons(side_length, screen):
  initial_hex = Hexagon(
    center=numpy.array([(MAX_X/2, MAX_Y/2)]).T,
    northern_most_unit_vector_direction=numpy.array([(0, 1)]).T,
    side_length=side_length
  )
  initial_hex.draw(screen)
  recursive_draw_hexagons(initial_hex, screen, 1)
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

  pygame.init()
  screen = pygame.display.set_mode((MAX_X, MAX_Y))
  draw_all_hexagons(
    side_length=50,
    screen=screen
  )

  pygame.display.update()
  while True:
    for event in pygame.event.get(): 
      if event.type == pygame.QUIT: 
        sys.exit(0) 
      else:
        print(event)

