# NOTE: Pygame has the origin of (x, y) = (0, 0) in the top-left corner, with
#  x increasing from left to right, and y increasing from up to down.
#  Thus, the northern-most vertex of a hexagon drawn in this manner will have
#  a y-value less than the center of the hexagon.
import numpy
import math
import random
import time
import pygame
from shapely.geometry import Point
random.seed(time.time())

from settings import X_RES
from settings import Y_RES


from hexagon import Hexagon
class BaseLocationManager(Hexagon):
  def __init__(self, *args, **kwargs):
    # Don't worry about understanding this, just add this to your 
    Hexagon.__init__(self, *args, **kwargs)
    self.registered_phones = {}


  def register(self, phone, child_caller=None):
    pass


  def unregister(self, phone):
    pass


  def dark_spot_deregister(self, phone):
    print("{0} - DARK SPOT DEREGISTER for {1} at {2}".format(
      self.depth,
      phone.id,
      id(self)
    ))
    del self.registered_phones[phone.id]

    if self.parent is not None:
      self.parent.dark_spot_deregister(phone)


class BasicPointerLocationManager(BaseLocationManager):
  def register(self, phone, child_caller=None):
    print("{0} - REGISTER of {1} at {2}".format(
      self.depth,
      phone.id,
      id(self)
    ))
    # When the phone ID is first in the database of the registration area,
    #  then we have found the Least Common Ancestor of the old and new
    #  registration areas.
    if phone.id in self.registered_phones:
      # The LCA does not need to be updated since it does have the phone
      #  within its subtree registration areas. However, since the current
      #  record is pointing to another registration area that is not accurate,
      #  then we need to unregister it, along with all other registration areas
      #  underneath it.
      print("{0} - REGISTER found LCA of {1} at {2}".format(
        self.depth,
        phone.id,
        id(self)
      ))
      self.unregister(phone)
    elif self.parent is not None:
      print("{0} - REGISTER did not find {1} at {2}".format(
        self.depth,
        phone.id,
        id(self)
      ))
      self.parent.register(phone, self)

    # We do need to update the LCA to point to the correct RA within its
    #  subtree.
    #if self.internal_hexagons[0].initialized:
    if child_caller is None:
      # If the child caller is None, then this cell is a low-level cell and
      #  should point to the phone.
      print("{0} - REGISTER set cell site of {1} at {2}".format(
        self.depth,
        phone.id,
        id(self)
      ))
      self.registered_phones[phone.id] = phone

    else:
      # The child caller should be set to the new pointer in the database.
      print("{0} - REGISTER set for {1}: {2} -> {3}".format(
        self.depth,
        phone.id,
        id(self),
        id(child_caller)
      ))
      self.registered_phones[phone.id] = child_caller


  def unregister(self, phone):
    print("{0} - UNREGISTER initialized for {1} at {2}".format(
      self.depth,
      phone.id,
      id(self)
    ))
    ptr = self.registered_phones[phone.id]

    # Check to see if the current registration area is actually a PCS cell.
    #  If it is a PCS cell, then there are no other registration areas under
    #  it, and thus unregistration must continue.
    if ptr != phone:
      print("{0} - UNREGISTER found a pointer: {1} -> {2}".format(
        self.depth,
        id(self),
        id(ptr)
      ))
      ptr.unregister(phone)

    print("{0} - UNREGISTER deleted record of {1}: {2} -x-> {3}".format(
      self.depth,
      phone.id,
      id(self),
      id(self.registered_phones[phone.id])
    ))
    del self.registered_phones[phone.id]


def draw_all_hexagons(center, side_length):
  center_point = numpy.array([(center)]).T
  # Create all hexagons within the viewing window.
  root_hexagon = BasicPointerLocationManager(
    center=center_point,
    northern_most_unit_vector_direction=numpy.array([(0, 1)]).T,
    side_length=side_length
  )
  root_hexagon.draw()
  level_1_hexagons = root_hexagon.create_internal_hexagons()
  level_2_hexagons = []
  for h in level_1_hexagons:
    h.draw()
    level_2_hexagons.extend(h.create_internal_hexagons())

  for h in level_2_hexagons:
    h.draw()

  for h in level_2_hexagons:
    h.draw(color=(0,0,0), width=1)
  for h in level_1_hexagons:
    h.draw(color=(0,0,0), width=1)

  hexagons = [
    [root_hexagon],
    level_1_hexagons,
    level_2_hexagons
  ]
  return hexagons


from utils import transform_points_for_pygame
class Phone(pygame.sprite.Sprite, Point):
  movement_offset = 10

  def __init__(self, char, center, cells):
    pygame.sprite.Sprite.__init__(self)
    Point.__init__(self, center)

    # This is the unique name/address of the phone.
    self.id = char

    # These are all of the PCS cells in which this phone can be within.
    self.cells = cells

    # This is the geographic cell in which the phone is within. The center of
    #  this cell has a base station with which this phone can connect with
    #  to make calls, register its location, etc.
    self.PCS_cell = None
    for h in self.cells:
      if h.contains(self):
        self.PCS_cell = h
        h.register(self)

    # These member variables are required for this Phone class to be a
    #  sprite.
    self.image = pygame.image.load("phone.png").convert_alpha()
    self.rect = self.image.get_rect()
    self.rect.center = transform_points_for_pygame([center])[0]

    # If the phone is moved, the offset vector will be updated. It is a
    #  direction vector.
    self.offset = (0,0)

    # The label is drawn on top of the sprite.
    label_font = pygame.font.SysFont("monospace", 15)
    self.label = label_font.render(char, True, (255, 255, 255))
    self.draw_text()


  # This function is called by the RenderGroup object with which this phone is
  #  a member of.
  def update(self):
    x, y = self.coords[0]
    center = (
      x + self.movement_offset*self.offset[0],
      y + self.movement_offset*self.offset[1]
    )
    self.rect.center = transform_points_for_pygame([center])[0]
    self._set_coords(center)
    self.offset = (0,0)


  def draw_text(self):
    x = self.label.get_width()
    y = self.label.get_height()
    self.image.blit(self.label, (x, y))


  def move_by(self, offset_vector):
    self.offset = offset_vector


  def has_moved_to_new_cell(self):
    if self.PCS_cell is None:
      for h in self.cells:
        if h.contains(self):
          print("{0} has moved".format(self.id))
          return True
      return False

    else:
      if self.PCS_cell.contains(self):
        return False
      else:
        print("{0} has moved".format(self.id))
        return True

  def update_location(self):
    # It is assumed that the phone has updated its location, which is one of
    #  the possible update scenarios:
    #  1. None -> Cell
    #  2. Cell -> Cell
    #  3. Cell -> None
    if self.PCS_cell is None:
      #  1. None -> Cell
      for h in self.cells:
        if h.contains(self):
          self.PCS_cell = h
          h.register(self)
          return

    else:
      #  2. Cell -> Cell
      #  3. Cell -> None
      old_cell = self.PCS_cell
      self.PCS_cell = None
      for h in self.cells:
        if h.contains(self):
          self.PCS_cell = h
          h.register(self)

      if self.PCS_cell is None:
        # The phone has roamed out of its coverage area, and thus should
        #  perform a dark area deregister.
        old_cell.dark_spot_deregister(self)


if __name__ == "__main__":
  import sys
  pygame.init()
  screen = pygame.display.set_mode((X_RES, Y_RES))
  BACKGROUND_COLOR = (127, 127, 127)
  screen.fill(BACKGROUND_COLOR)

  # Create every hexagon on each level.
  hexagons = draw_all_hexagons(
    center=(X_RES/2, Y_RES/2),
    side_length=Y_RES/2
  )
  PCS_cells = hexagons[-1]
  current_depth = len(hexagons)-1
  current_depth_hexagons = hexagons[current_depth]

  phone_labels = ['a', 'b', 'c', 'd', 'e']
  random_coord_within_screen = lambda coords: [
    random.randint(0, coords[i]) for i in range(2)
  ]

  phone_dict = {}
  for l in phone_labels:
    phone_dict[l] = Phone(
      char=l.upper(),
      center=random_coord_within_screen((X_RES, Y_RES)),
      cells=PCS_cells
    )

  selected_phone = phone_dict['a']

  # Draw each phone on the screen.
  for k in phone_dict:
    p = phone_dict[k]
    screen.blit(p.image, p.rect)

  # Phones need to be added to a render group so that they're updated whenever
  #  they move.
  phones = pygame.sprite.RenderUpdates(phone_dict.values())

  pygame.display.update()

  while True:
    for event in pygame.event.get(): 
      if event.type == pygame.QUIT: 
        sys.exit(0) 
      elif event.type == pygame.KEYDOWN:

        # Erase the entire screen for preparation of redrawing.
        screen.fill(BACKGROUND_COLOR)

        # If the Minus key is pressed, interpret this as the user wants to
        #  visualize the the depth that is above the currently displayed depth.
        #  In other words, if current depth = i, display depth i-1.
        if event.key == pygame.K_MINUS:
          if current_depth > 0:
            current_depth -= 1

        elif event.key == pygame.K_EQUALS:
          if current_depth < len(hexagons)-1:
            current_depth += 1

        # If the arrow keys are pressed, then we assume the user wants to move
        #  the currently selected phone in the direction of the key.
        elif event.key == pygame.K_UP:
          selected_phone.move_by((0, 1))

        elif event.key == pygame.K_DOWN:
          selected_phone.move_by((0, -1))

        elif event.key == pygame.K_RIGHT:
          selected_phone.move_by((1, 0))

        elif event.key == pygame.K_LEFT:
          selected_phone.move_by((-1, 0))

        # Test if one of the cell phone labels have been selected.
        elif event.key in [ord(k) for k in phone_labels]:
          # We now need to determine if the user is selecting a cell phone, or
          #  if they are calling a cell phone.
          key = chr(event.key)

          # Test if the Ctrl button is selected. This implies the user is
          #  calling another cell phone.
          if pygame.key.get_mods() & pygame.KMOD_CTRL:
            # One of the Ctrl keys is being pressed. This represents a call.
            # The phone initiating the call is the currently selected phone.
            # We must now make sure the callee is not the same as the caller.
            callee = phone_dict[key]
            if callee != selected_phone:
              print("{0} calling {1}".format(selected_phone.id, callee.id))
            else:
              print("Calling yourself? How odd...")

          else:
            # The user is pressing only one key, which is a label for another
            #  phone. Make this phone the currently selected phone.
            print("Changing focus from {0} to {1}".format(
              selected_phone.id, key
            ))
            selected_phone = phone_dict[key]

        # Redraw the hexagons that are on the currently selected depth.
        current_depth_hexagons = hexagons[current_depth]
        for h in current_depth_hexagons:
          h.draw()

        # Check to see if the phone is still in the previously set cell.
        if selected_phone.has_moved_to_new_cell():
          selected_phone.update_location()

        cell = selected_phone.PCS_cell
        if cell is not None:
          cell.draw(color=(255,255,255), width=5)

        for h in current_depth_hexagons:
          # Determine which hexagon currently contains the selected phone.
          if h != selected_phone.PCS_cell:
            h.draw(color=(0,0,0), width=2)
          else:
            h.draw(color=(255,255,255), width=5)

        # Draw all of the phones to the screen.
        phones.update()
        phones.draw(screen)
        pygame.display.update()

      else:
        print(event)
