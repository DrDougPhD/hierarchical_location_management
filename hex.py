# NOTE: Pygame has the origin of (x, y) = (0, 0) in the top-left corner, with
#  x increasing from left to right, and y increasing from up to down.
#  Thus, the northern-most vertex of a hexagon drawn in this manner will have
#  a y-value less than the center of the hexagon.

def recursive_draw_hex():
  initial_hex = Hexagon((0,0))
  east_hex = initial_hex.create_hex_to_east()
  southeast_hex = initial_hex.create_hex_to_southeast()
  southwest_hex = initial_hex.create_hex_to_southwest()
  

class Hexagon:
  def __init__(self, center, northern_most_vertex, side_length, distance_from_center_to_midpoint_of_side):
    dx = distance_from_center_to_midpoint_of_side
    dy = side_length
    x, y = center
    self.center = (x, y)

    yd2 = dy/2
    self.north = tuple(northern_most_vertex)
    self.northeast = (x+dx, y-yd2)
    self.southeast = (x+dx, y+yd2)
    self.south = (x, y+dy)
    self.southwest = (x-dx, y+yd2)
    self.northwest = (x-dx, y-yd2)


  def draw(self):
    pass

def create_hex_grid(max_x, max_y, hex_side_length,
                    distance_from_center_to_midpoint_of_side):
  x = distance_from_center_to_midpoint_of_side
  y = hex_side_length

  initial_hex = Hexagon(
    center=(0,0),
    northern_most_vertex=(0, -y),
    hex_side_length=y,
    distance_from_center_to_midpoint_of_side=x
  )


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
  create_hex_grid(
    max_x=640,
    max_y=480,
    hex_side_length=45,
    distance_from_center_to_midpoint_of_side=26
  )
