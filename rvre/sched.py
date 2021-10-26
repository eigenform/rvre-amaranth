
from nmigen import *
from nmigen.hdl.rec import *
from nmigen.sim import *

class ReservationStation(Elaboratable):
    """ A "reservation station."
    Buffer for parked instructions (waiting on data dependencies).
    """
    def __init__(self):
        pass
    def elaborate(self, platform):
        m = Module()
        return m

class ReorderBuffer(Elaboratable):
    """ A "re-order buffer" (ROB).
    Buffer for in-order (program order) instruction retiry.
    """
    def __init__(self):
        pass
    def elaborate(self, platform):
        m = Module()
        return m

class RegisterAliasTable(Elaboratable):
    """ A "register alias table" (RAT). 
    Map from architectural registers to ROB entries.
    """
    def __init__(self):
        pass
    def elaborate(self, platform):
        m = Module()
        return m


