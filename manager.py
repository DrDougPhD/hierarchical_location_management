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
    phone.num_writes += 1
    del self.registered_phones[phone.id]

    if self.parent is not None:
      self.parent.dark_spot_deregister(phone)


  def search_for(self, callee, caller, trace=None):
    # Callee is the unique name of the phone being called.
    # Caller is the phone object placing the call.
    if trace is None:
      trace = "{0} -> {1} (depth {2})".format(caller.id, id(self), self.depth)
    else:
      trace = "{0} -> {1} (depth {2})".format(trace, id(self), self.depth)

    caller.num_reads += 1
    if callee in self.registered_phones:
      record = self.registered_phones[callee]
      print("Record: {0}".format(record))
      if type(record) is BaseLocationManager:
        # If the record points to a Registration Area, then we have not found
        #  the cell containing the phone yet and must continue searching.
        print("RA record for {0} is found from {1} (depth {2}) -> {3} (depth"
              " {4}). Following pointer.".format(
          callee,
          id(self),
          self.depth,
          id(record),
          record.depth
        ))
        record.search_for(callee, caller, trace)

      else:
        print("Cell for {0} is found at {1} (depth {2}). Connecting call for"
              " {3} -> {0}".format(
          callee,
          id(self),
          self.depth,
          caller.id
        ))
        print("Call trace: {0} -> {1}".format(trace, callee))

    elif self.parent is not None:
      self.parent.search_for(callee, caller, trace)

    else:
      print("Callee {0} is not registered in the network. VOICEMAIL.".format(
        callee
      ))
      print("Call trace: {0} -> VOICEMAIL".format(trace))


class BasicPointerLocationManager(BaseLocationManager):
  # Each Registration Area has records for the phones within its registration
  #  area, where the values associated with the phone IDs are pointers to the
  #  smaller registration area immediately below it.
  def register(self, phone, child_caller=None):
    print("{0} - REGISTER of {1} at {2}".format(
      self.depth,
      phone.id,
      id(self)
    ))
    # When the phone ID is first in the database of the registration area,
    #  then we have found the Least Common Ancestor of the old and new
    #  registration areas.
    phone.num_reads += 1
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
      phone.num_writes += 1
      self.registered_phones[phone.id] = phone

    else:
      # The child caller should be set to the new pointer in the database.
      print("{0} - REGISTER set for {1}: {2} -> {3}".format(
        self.depth,
        phone.id,
        id(self),
        id(child_caller)
      ))
      phone.num_writes += 1
      self.registered_phones[phone.id] = child_caller


  def unregister(self, phone):
    print("{0} - UNREGISTER initialized for {1} at {2}".format(
      self.depth,
      phone.id,
      id(self)
    ))
    phone.num_reads += 1
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
    phone.num_writes += 1
    del self.registered_phones[phone.id]


class BasicValueLocationManager(BaseLocationManager):
  # Each registration area will have the absolute cell ID associated with the
  #  phones that are within its registration area.
  def register(self, phone, cell_of_caller=None):
    print("{0} - REGISTER of {1} at {2}".format(
      self.depth,
      phone.id,
      id(self)
    ))

    cell_to_update = None
    if cell_of_caller is None:
      cell_of_caller = self
    # All registration areas above this registration area must be updated.
    phone.num_reads += 1
    if phone.id in self.registered_phones:
      print("{0} - REGISTER found pre-existing record for {1} at {2} (-> {3})".format(
        self.depth,
        phone.id,
        id(self),
        id(self.registered_phones[phone.id])
      ))
      cell_to_update = self.registered_phones[phone.id]

    phone.num_writes += 1
    self.registered_phones[phone.id] = cell_of_caller
    print("{0} - REGISTER: For {1}, {2} -> {3}".format(
      self.depth,
      phone.id,
      id(self),
      id(cell_of_caller)
    ))

    if self.parent is not None:
      self.parent.register(phone, cell_of_caller)
    elif cell_to_update is not None:
      cell_to_update.unregister(phone)


  def unregister(self, phone, old_cell=None):
    print("{0} - UNREGISTER of {1} at {2}".format(
      self.depth,
      phone.id,
      id(self)
    ))

    if old_cell is None:
      old_cell = self
      phone.num_writes += 1

      print("{0} - UNREGISTER of {1}: {2} -x-> {3}".format(
        self.depth,
        phone.id,
        id(self),
        id(self.registered_phones[phone.id])
      ))
      del self.registered_phones[phone.id]

    if self.parent is not None:
      phone.num_reads += 1
      if self.parent.registered_phones[phone.id] == old_cell:
        phone.num_writes += 1
        print("{0} - UNREGISTER parent of {1}: {2} -x-> {3}".format(
          self.depth,
          phone.id,
          id(self.parent),
          old_cell
        ))
        del self.parent.registered_phones[phone.id]
        self.parent.unregister(phone, old_cell)

