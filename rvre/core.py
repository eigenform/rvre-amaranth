
from amaranth import *
from amaranth.sim import *
from amaranth.lib.fifo import *
from amaranth.hdl.ast import Array

from functools import reduce
from itertools import starmap
from operator import or_

from .common import *
from .fetch import *
from .decode import *
from .issue import *
from .rf import *

from .alu import *
from .lsu import *
from .bru import *


FMT_RD  = (InstFormat.R, InstFormat.I, InstFormat.U, InstFormat.J)
FMT_RS1 = (InstFormat.R, InstFormat.I, InstFormat.S, InstFormat.B)
FMT_RS2 = (InstFormat.R, InstFormat.S, InstFormat.B)

class RVRECore(Elaboratable):
    PHYS_REGS = 64

    def __init__(self, reset_vector=0x00000000, rom_data=None):
        self._rom_data = rom_data

        # The initial program counter value
        self.reset = reset_vector

        self.ifu = FetchUnit(rom_data=rom_data)
        self.idu = Decoder()
        self.rat = RegisterAliasTable(self.PHYS_REGS)
        self.prf = PhysicalRegisterFile(self.PHYS_REGS)

        self.alu = ALU()

    def ports(self):
        return []

    def elaborate(self, platform):
        m = Module()

        r_pc   = Signal(32, reset=self.reset - 4)
        r_inst = Signal(32)

        m.submodules.fetch  = ifu = self.ifu
        m.submodules.decode = idu = self.idu
        m.submodules.rat    = rat = self.rat
        m.submodules.prf    = prf = self.prf
        m.submodules.alu    = alu = self.alu

        # Fetch unit buffered inputs
        m.d.comb += ifu.i_pc.eq(r_pc)

        # Decode unit buffered inputs
        m.d.comb += idu.i_inst.eq(r_inst),

        # Determine which register operands are used for this uop.
        rd_en  = Signal()
        rs1_en = Signal()
        rs2_en = Signal()
        m.d.comb += [
            rd_en.eq( reduce(or_, (idu.o_ifmt == F for F in FMT_RD))),
            rs1_en.eq(reduce(or_, (idu.o_ifmt == F for F in FMT_RS1))),
            rs2_en.eq(reduce(or_, (idu.o_ifmt == F for F in FMT_RS2))),
        ]

        # Get the physical registers mapped to RS1/RS2.
        pd  = Signal(PhysReg)
        ps1 = Signal(PhysReg)
        ps2 = Signal(PhysReg)
        m.d.comb += [
            rat.rp1.en.eq(rs1_en),
            rat.rp2.en.eq(rs2_en),
            rat.rp1.addr.eq(idu.o_rs1), 
            rat.rp2.addr.eq(idu.o_rs2),
            ps1.eq(rat.rp1.data),
            ps2.eq(rat.rp2.data),
        ]

        # Allocate a physical register for RD
        m.d.comb += [
        ]

        # Latch next program counter
        m.d.sync += r_pc.eq(r_pc + 4)
        # Latch next instruction
        m.d.sync += r_inst.eq(ifu.o_inst)

        return m


