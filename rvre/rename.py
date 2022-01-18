
from enum import Enum, unique

from amaranth import *
from amaranth.hdl.rec import *
from amaranth.lib.coding import Encoder, Decoder, PriorityEncoder

from .param import *
from .common import *

__all__ = [ "RegisterAliasTable", "RegisterBusyTable", "RegisterFreeTable" ]

class RegisterAliasTable(Elaboratable):
    """ Map from architectural registers to physical registers. """
    _rd_port_layout = Layout([ 
        ("areg", ArchReg), ("preg", PhysReg) 
    ])
    _wr_port_layout = Layout([
        ("en", 1), ("areg", ArchReg), ("preg", PhysReg)
    ])

    def __init__(self, arf_size, prf_size):
        self.arf_size = arf_size
        self.prf_size = prf_size
        self.rat = Array(Signal(PhysReg, reset=idx) for idx in range(arf_size))
        self.rp1 = Record(self._rd_port_layout)
        self.rp2 = Record(self._rd_port_layout)
        self.wp1 = Record(self._wr_port_layout)

    def elaborate(self, platform):
        m = Module()
        m.d.comb += [
            self.rp1.preg.eq(self.rat[self.rp1.areg]),
            self.rp2.preg.eq(self.rat[self.rp2.areg])
        ]
        with m.If(self.wp1.en):
            m.d.sync += self.rat[self.wp1.areg].eq(self.wp1.preg)
        return m

class RegisterBusyTable(Elaboratable):
    """ Busy table for physical registers (one bit per register).
    The 'busy' bit for a physical register is set after being allocated, then 
    cleared after a result is written back to the physical register file.
    """
    _commit_layout = Layout([ ("prd", PhysReg), ("en", 1) ])
    _alloca_layout = Layout([ ("prd", PhysReg), ("en", 1) ])
    _wakeup_layout = Layout([
        ("ps1", PhysReg), ("ps2", PhysReg),
        ("ps1_busy", 1), ("ps2_busy", 1),
    ])

    def __init__(self, prf_size):
        self.prf_size = prf_size

        self.dec0 = Decoder(prf_size)
        self.dec1 = Decoder(prf_size)

        self.enc0 = Encoder(prf_size)
        self.enc1 = Encoder(prf_size)

        self.busytbl = Signal(prf_size)

        self.commit = Record(self._commit_layout)
        self.alloc  = Record(self._alloca_layout)
        self.wakeup = Record(self._wakeup_layout)

    def elaborate(self, platform):
        m = Module()

        m.submodules.dec0 = dec0 = self.dec0
        m.submodules.dec1 = dec1 = self.dec1
        m.submodules.enc0 = enc0 = self.enc0
        m.submodules.enc1 = enc1 = self.enc1

        ps1_sel = Signal(self.prf_size)
        ps2_sel = Signal(self.prf_size)
        m.d.comb += [
            enc0.i.eq(self.wakeup.ps1),
            ps1_sel.eq(enc0.o),

            enc1.i.eq(self.wakeup.ps2),
            ps2_sel.eq(enc1.o),

            self.wakeup.ps1_busy.eq(self.busytbl & ps1_sel),
            self.wakeup.ps2_busy.eq(self.busytbl & ps2_sel),
        ]

        commit_mask = Signal(self.prf_size)
        alloc_bits  = Signal(self.prf_size)

        m.d.comb += [
            dec0.n.eq(~self.commit.en),
            dec0.i.eq(self.commit.prd), 
            commit_mask.eq(~dec0.o),

            dec1.n.eq(~self.alloc.en),
            dec1.i.eq(self.alloc.prd), 
            alloc_bits.eq(dec1.o),
        ]

        m.d.sync += self.busytbl.eq( 
            (self.busytbl & commit_mask) | alloc_bits 
        )
        return m

class RegisterFreeTable(Elaboratable):
    """ Free table for physical registers.
    """
    _allocate_layout = Layout([ ("en", 1), ("prd", PhysReg), ("ok", 1) ])
    _free_layout = Layout([ ("prd", PhysReg), ("en", 1) ])

    def __init__(self, prf_size):
        self.prf_size = prf_size
        self.freetbl = Signal(prf_size, reset=~1)

        self.enc = PriorityEncoder(prf_size)
        self.dec0 = Decoder(prf_size)
        self.dec1 = Decoder(prf_size)

        self.alloc = Record(self._allocate_layout)
        self.free  = Record(self._allocate_layout)

    def elaborate(self, platform):
        m = Module()

        m.submodules.enc = enc = self.enc
        m.submodules.dec0 = dec0 = self.dec0
        m.submodules.dec1 = dec1 = self.dec1

        alloc_res = Signal(PhysReg)
        alloc_valid = Signal()
        alloc_ok = Signal()

        alloc_bits = Signal(self.prf_size)
        free_mask  = Signal(self.prf_size)

        m.d.comb += [
            enc.i.eq(self.freetbl),
            alloc_res.eq(enc.o),
            alloc_valid.eq(~enc.n),
            alloc_ok.eq(alloc_valid & self.alloc.en),

            self.alloc.ok.eq(alloc_ok),
            self.alloc.prd.eq(alloc_res),

            dec0.i.eq(alloc_res),
            dec0.n.eq(~alloc_ok),
            alloc_bits.eq(dec0.o),

            dec1.i.eq(self.free.prd),
            dec1.n.eq(~self.free.en),
            free_mask.eq(~dec1.o),
        ]

        m.d.sync += self.freetbl.eq(
            (self.freetbl & free_mask) | alloc_bits
        )

        return m



