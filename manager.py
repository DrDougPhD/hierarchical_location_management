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

