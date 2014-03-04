from hexagon import Hexagon
from collections import defaultdict
class BaseLocationManager(Hexagon):
  def __init__(self, *args, **kwargs):
    # Don't worry about understanding this, just add this to your 
    Hexagon.__init__(self, *args, **kwargs)
    self.registered_phones = {}

    # local_calls is a dictionary, keyed on the phone's id, valued at
    #  the number of calls made to the phone from all cells within this
    #  registration area.
    self.local_calls = defaultdict(int)

    # mobility is a dictionary, keyed on the phone's id, valued at
    #  the number of movements made by the phone.
    self.phone_mobility = {}


  def update_location(self, phone):
    # The phone has entered this cell, and needs to register. This should kick
    #  a recursive registration.
    phone.num_writes += 1
    self.registered_phones[phone.id] = phone
    print("{0} - REGISTER for {1} at call: {2} -> {1}".format(
      self.depth,
      phone.id,
      id(self)
    ))
    self.recursive_update_mobility(phone)
    self.parent.register(phone, self)


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
      if isinstance(record, BaseLocationManager):
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


  def recursive_increment_local_calls(self, callee):
    if callee in self.local_calls:
      self.local_calls[callee] += 1
    else:
      self.local_calls[callee] = 1

    print("{0}-{1}: {2} had {3} calls from this subtree".format(
      self.depth,
      id(self),
      callee,
      self.local_calls[callee]
    ))

    if self.parent is not None:
      self.parent.recursive_increment_local_calls(callee)


  def recursive_update_mobility(self, phone):
    if self.parent is not None:
      self.parent.recursive_update_mobility(phone)

    else:
      self.phone_mobility[phone.id] = phone.mobility
      for h in self.internal_hexagons:
        h.trickle_down_update_mobility(phone)


  def trickle_down_update_mobility(self, phone):
    self.phone_mobility[phone.id] = phone.mobility
    #print("{0}-{1}: {2} has moved {3} times".format(
    #  self.depth,
    #  id(self),
    #  phone.id,
    #  self.phone_mobility[phone.id]
    #))
    if self.internal_hexagons is not None:
      for h in self.internal_hexagons:
        h.trickle_down_update_mobility(phone)


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

    if phone.id in self.registered_phones:
        # This registration area is a parent of the cell of caller.

        # All registration areas above this registration area must be updated.
        phone.num_reads += 1
        print("{0} - REGISTER found pre-existing record for {1} at {2} (-> {3})".format(
          self.depth,
          phone.id,
          id(self),
          id(self.registered_phones[phone.id])
        ))
        self.registered_phones[phone.id].unregister(phone)

        # This record will be deleted in the unregister() procedure, and will
        #  be updated immediately once unregistering is complete. Thus, it is
        #  only considered as one write.

    else:
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


  def unregister(self, phone, old_cell=None):
    print("{0} - UNREGISTER of {1} at {2}".format(
      self.depth,
      phone.id,
      id(self)
    ))

    if old_cell is None:
      old_cell = self
      print("{0} - UNREGISTER of {1}: {2} -x-> {3}".format(
        self.depth,
        phone.id,
        id(self),
        id(self.registered_phones[phone.id])
      ))
      phone.num_writes += 1
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


class ReplicationLocationManager(BasicPointerLocationManager):
  S_min = 2
  S_max = 2
  def __init__(self, *args, **kwargs):
    BasicPointerLocationManager.__init__(self, *args, **kwargs)
    self.replicas = {}


  def search_for(self, callee, caller, trace=None):
    # Callee is the unique name of the phone being called.
    # Caller is the phone object placing the call.
    if trace is None:
      trace = caller.id

    trace = "{0} -> {1} (depth {2})".format(trace, id(self), self.depth)

    # 1. This RA has a replica of the callee.
    # 1a. This RA has a LCMR that satisfies the replica's presence.
    #  -> Call search on the replica.
    # 1b. This RA has an unsatisfactory LCMR.
    #  -> Delete the replica.
    # 2. This RA does not have a replica.
    # 2a. This RA has a record for the callee.
    # 2a1. This record points to another RA.
    #   -> Call search on the RA.
    # 2a2. This record points to the phone.
    #   -> End search.
    # 2b. This RA does not have a record for the callee.
    # 2b1. This RA has a parent.
    #   -> Call search on the parent.
    # 2b2. This RA does not have a parent.
    #   -> End search, callee not in coverage area.
    # If this RA has a sufficient LCMR, then store a replica.

    # The number of calls to the callee originating from this cell's subtree
    #  has already been updated.
    caller.num_reads += 1
    if callee in self.replicas:
      if self.replicas[callee] is not None:
        return self.replicas[callee].search_for(callee, caller, trace)

      else:
        # Not in coverage area.
        print("CALL TRACE: {0} -> VOICEMAIL".format(trace))
        return None

    else:
      if callee in self.registered_phones:
        record = self.registered_phones[callee]
        if isinstance(record, BaseLocationManager):
          cell_of_callee = record.search_for(callee, caller, trace)

        else:
          print("CALL TRACE: {0} -> {1}".format(
            trace,
            callee
          ))
          return self

      elif self.parent is not None:
        cell_of_callee = self.parent.search_for(callee, caller, trace)

      else:
        print("CALL TRACE: {0} -> VOICEMAIL".format(trace))
        cell_of_callee = None

      lcmr = self.local_calls[callee] / float(self.phone_mobility[callee])
      if lcmr > self.S_max:
        print("{0} - REPLICATING profile of {1} (located at {2}) to {3}".format(
          self.depth,
          callee,
          id(cell_of_callee) if cell_of_callee is not None else "NOWHERE",
          id(self)
        ))
        caller.num_writes += 1
        self.replicas[callee] = cell_of_callee

      return cell_of_callee


  #def register(self, phone):
  #  pass


  #def unregister(self, phone):
  #  pass


  def trickle_down_update_mobility(self, phone):
    phone.num_writes += 1
    self.phone_mobility[phone.id] = phone.mobility
    lcmr = self.local_calls[phone.id] / float(self.phone_mobility[phone.id])
    if lcmr > self.S_max:
      print("{0} - LCMR of {1} for phone {2} above threshold."
            " Creating replica. {3} > {4}".format(
        self.depth,
        id(self),
        phone.id,
        lcmr,
        self.S_max
      ))
      self.replicas[phone.id] = phone.PCS_cell

    elif lcmr < self.S_max and phone.id in self.replicas:
      print("{0} - LCMR of {1} for phone {2} below threshold."
            " Deleting replica. {3} < {4}".format(
        self.depth,
        id(self),
        phone.id,
        lcmr,
        self.S_max
      ))
      del self.replicas[phone.id]

    if self.internal_hexagons is not None:
      for h in self.internal_hexagons:
        h.trickle_down_update_mobility(phone)


class ForwardingPointerLocationManager(BasicPointerLocationManager):
  def __init__(self, *args, **kwargs):
    BasicPointerLocationManager.__init__(self, *args, **kwargs)
    self.phone_record_instantiated = defaultdict(bool)


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
      t = child_caller
      s = self.registered_phones[phone.id]
      s.unregister(phone)
      s.registered_phones[phone.id] = t
    elif self.parent is not None:
      print("{0} - REGISTER did not find {1} at {2}".format(
        self.depth,
        phone.id,
        id(self)
      ))
      self.parent.register(phone, self)

      # The child caller should be set to the new pointer in the database.
      print("{0} - REGISTER set for {1}: {2} -> {3}".format(
        self.depth,
        phone.id,
        id(self),
        id(child_caller)
      ))
      phone.num_writes += 1
      self.registered_phones[phone.id] = child_caller

    if not self.phone_record_instantiated[phone.id]:
      self.phone_record_instantiated[phone.id] = True
      # The child caller should be set to the new pointer in the database.
      print("{0} - REGISTER set for {1}: {2} -> {3}".format(
        self.depth,
        phone.id,
        id(self),
        id(child_caller)
      ))
      phone.num_writes += 1
      self.registered_phones[phone.id] = child_caller
