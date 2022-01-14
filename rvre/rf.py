""" Register files.


"""

from amaranth import *
from amaranth.hdl.rec import *
from amaranth.sim import *
from enum import Enum, unique

class PhysicalRegisterFile(Elaboratable):
    """ Unified physical register file.
    """
    def __init__(self, size):
        self.size = size
        self.mem  = Memory(width=32, depth=size)
        self.rp1  = self.mem.read_port()
        self.rp2  = self.mem.read_port()
        self.wp1  = self.mem.write_port()

    def elaborate(self, platform):
        m = Module()

        m.submodules.rp1 = rp1 = self.rp1
        m.submodules.rp2 = rp2 = self.rp2
        m.submodules.wp1 = wp1 = self.wp1

        return m

class RegisterAliasTable(Elaboratable):
    """ Map from architectural registers to physical registers.
    """
    def __init__(self, prf_size, arf_size=32):
        self.prf_size = prf_size
        self.arf_size = arf_size
        self.data = Memory(width=range(prf_size), depth=arf_size)
        self.rp1  = self.data.read_port()
        self.rp2  = self.data.read_port()
        self.wp1  = self.data.write_port()

    def elaborate(self, platform):
        m = Module()

        m.submodules.rp1 = rp1 = self.rp1
        m.submodules.rp2 = rp2 = self.rp2
        m.submodules.wp1 = wp1 = self.wp1

        return m


