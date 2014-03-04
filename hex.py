# NOTE: Pygame has the origin of (x, y) = (0, 0) in the top-left corner, with
#  x increasing from left to right, and y increasing from up to down.
#  Thus, the northern-most vertex of a hexagon drawn in this manner will have
#  a y-value less than the center of the hexagon.
import numpy
import math
import random
import time
import pygame
random.seed(time.time())

from settings import X_RES
from settings import Y_RES
from manager import BasicPointerLocationManager
from manager import BasicValueLocationManager
from manager import ReplicationLocationManager
from manager import ForwardingPointerLocationManager
from phone import Phone

def draw_all_hexagons(center, side_length, location_manager):
  center_point = numpy.array([(center)]).T
  # Create all hexagons within the viewing window.
  #root_hexagon = BasicPointerLocationManager(
  #root_hexagon = BasicValueLocationManager(
  #root_hexagon = ReplicationLocationManager(
  #root_hexagon = ForwardingPointerLocationManager(
  root_hexagon = location_manager(
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

if __name__ == "__main__":
  import sys
  pygame.init()

  from manager import BasicPointerLocationManager
  from manager import BasicValueLocationManager
  from manager import ReplicationLocationManager
  from manager import ForwardingPointerLocationManager

  location_manager_index = int(sys.argv[-1])
  location_managers = [
    BasicPointerLocationManager,
    BasicValueLocationManager,
    ReplicationLocationManager,
    ForwardingPointerLocationManager
  ]
  location_manager = location_managers[location_manager_index]
  print("Location manager set to {0}".format(location_manager.__name__))

  screen = pygame.display.set_mode((X_RES, Y_RES))
  BACKGROUND_COLOR = (127, 127, 127)
  screen.fill(BACKGROUND_COLOR)

  # Create every hexagon on each level.
  hexagons = draw_all_hexagons(
    center=(X_RES/2, Y_RES/2),
    side_length=Y_RES/2,
    location_manager=location_manager
  )
  PCS_cells = hexagons[-1]
  current_depth = len(hexagons)-1
  current_depth_hexagons = hexagons[current_depth]

  phone_labels = ['a', 'b', 'c', 'd', 'e']
  random_coord_within_screen = lambda coords: [
    random.randint(0, coords[i]) for i in range(2)
  ]
  phone_locations = [
    (X_RES/2., Y_RES/2.),
    (X_RES/2., Y_RES/3.),
    (X_RES/3., Y_RES*3/4.),
    (X_RES*9/11., Y_RES/4.),
    (X_RES/4., Y_RES*4/5.)
  ]

  phone_dict = {}
  for l in phone_labels:
    phone_dict[l] = Phone(
      char=l.upper(),
      center=phone_locations[phone_labels.index(l)],#random_coord_within_screen((X_RES, Y_RES)),
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
        def write_out_results(location_manager, phones):
          num_searches = 0
          num_updates = 0
          for k in phones:
            num_updates += phones[k].num_writes
            num_searches += phones[k].num_reads

          with open(location_manager + "_results.txt", "w") as f:
            f.write(location_manager + "\n")
            f.write("Number of searches: {0}\n".format(num_searches))
            f.write("Number of updates:  {0}\n".format(num_updates))

        write_out_results(
          location_manager=location_manager.__name__,
          phones=phone_dict
        )
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
              selected_phone.call(callee.id)
              print("Cost: Reads := {0}, Writes := {1}".format(
                selected_phone.num_reads,
                selected_phone.num_writes
              ))

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

          print("Cost: Reads := {0}, Writes := {1}".format(
            selected_phone.num_reads,
            selected_phone.num_writes
          ))

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

      #else:
      #  print(event)
