
from amaranth import *
from amaranth.sim import *
from amaranth.lib.fifo import *

from .common import *
from .param import *

from .fetch import *
from .decode import *
from .rename import *


class RVRECore(Elaboratable):
    """ Representing an RV32I hardware thread.
    """

    def __init__(self, reset_vector=0x00000000, rom_data=None):
        self._rom_data = rom_data
        self.reset = reset_vector

        self.ifu = FetchUnit(rom_data=rom_data)
        self.idu = DecodeUnit()
        self.rat = RegisterAliasTable(PARAM.arf_size, PARAM.prf_size)
        self.rbt = RegisterBusyTable(PARAM.prf_size)
        self.rft = RegisterFreeTable(PARAM.prf_size)


    def ports(self):
        return []

    def elaborate(self, platform):
        m = Module()

        r_pc   = Signal(32, reset=self.reset - 4)
        r_inst = Signal(32)
        r_uop  = Record(Uop())

        m.submodules.ifu = ifu = self.ifu
        m.submodules.idu = idu = self.idu
        m.submodules.rat = rat = self.rat
        m.submodules.rbt = rbt = self.rbt
        m.submodules.rft = rft = self.rft

        # Fetch unit buffered inputs
        m.d.comb += ifu.i_pc.eq(r_pc)

        # Decode unit buffered inputs
        m.d.comb += idu.i_inst.eq(r_inst)

        # Destination register rename (physical register allocation)
        prd = Signal(PhysReg)
        m.d.comb += [
            rft.alloc.en.eq(idu.o_rd_en),
            prd.eq(rft.alloc.prd),

            rat.wp1.en.eq(idu.o_rd_en & rft.alloc.ok),
            rat.wp1.areg.eq(idu.o_rd),
            rat.wp1.preg.eq(prd),

            rbt.alloc.en.eq(idu.o_rd_en & rft.alloc.ok),
            rbt.alloc.prd.eq(prd),
        ]

        # Source register rename (physical register resolution)
        ps1 = Signal(PhysReg)
        ps2 = Signal(PhysReg)
        m.d.comb += [
            rat.rp1.areg.eq(idu.o_rs1),
            rat.rp2.areg.eq(idu.o_rs2),
            ps1.eq(rat.rp1.preg),
            ps2.eq(rat.rp2.preg),
        ]

        uop = Record(Uop())
        m.d.comb += [
            uop.op.eq(idu.o_op),
            uop.alu_op.eq(idu.o_alu_op),
            uop.lsu_op.eq(idu.o_lsu_op),
            uop.bru_op.eq(idu.o_bru_op),
            uop.rd.eq(idu.o_rd),
            uop.prd.eq(prd),
            uop.ps1.eq(ps1),
            uop.ps2.eq(ps2),
        ]


        # Latch next program counter
        m.d.sync += r_pc.eq(r_pc + 4)
        # Latch next instruction
        m.d.sync += r_inst.eq(ifu.o_inst)
        # Latch next uop
        m.d.sync += r_uop.eq(uop)

        return m


