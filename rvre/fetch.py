
from amaranth import *
from amaranth.sim import *
from amaranth.hdl.rec import *

from math import ceil, log2

class FetchUnit(Elaboratable):
    """ Instruction fetch unit """
    ROM_SIZE = 32

    def __init__(self, rom_data=None):
        self.rom    = Memory(width=32, depth=self.ROM_SIZE, init=rom_data)
        self.addr   = Signal(ceil(log2(self.ROM_SIZE)))
        self.i_pc   = Signal(32)
        self.o_inst = Signal(32)
        pass

    def elaborate(self, platform):
        m = Module()

        m.submodules.rp = rp = self.rom.read_port()

        # NOTE: This ROM is word-addressible (hence the left-shift).
        m.d.comb += [
            self.addr.eq((self.i_pc >> 2)[0:5]),
            rp.addr.eq(self.addr),
            self.o_inst.eq(rp.data),
        ]

        return m

