

from amaranth import *
from amaranth.sim import *
from amaranth.hdl.rec import *


class PipelineStage(Elaboratable):
    """ Module for managing pipeline registers.

    """
    def __init__(self, upstream, **ds_layout):
        # Optional link to the previous pipeline stage
        self.upstream = upstream

        # Set of pipeline registers
        self._layout = []
        for sig in ds_layout.items():
            self._layout.append((sig[0], sig[1], DIR_NONE))

        # Automatically propagate similarly-named registers from upstream
        # NOTE: Are there any signals where you *don't* want to do this?
        self._propagate = []
        if self.upstream != None:
            self._propagate = [
                sig for sig in self._layout if sig in self.upstream._layout
            ]

        # Pipeline register control signals
        self.stall = Signal()
        self.valid = Signal()
        
        # Pipeline registers associated with this stage
        self.ds    = Record(self._layout)

    def elaborate(self, platform):
        m = Module()


        if self.upstream is not None:
            m.d.comb += [
                self.valid.eq(self.upstream.valid),
                self.upstream.stall.eq(self.stall),
            ]

        # Propagate registers from upstream
        #with m.If(~self.stall):
        #    for x in self._propagate:
        #        m.d.comb += self.ds[x[0]].eq(self.upstream.ds[x[0]])

        return m


