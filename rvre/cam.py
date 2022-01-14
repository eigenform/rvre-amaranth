
from amaranth import *
from amaranth.lib.coding import Encoder
from enum import Enum, unique

@unique
class CAMOp(Enum):
    IDLE  = 0
    READ  = 1
    WRITE = 2


class CAM(Elaboratable):
    """ Naive generic content-addressable memory, I guess.
    'i_en': Enable broadcasts to all entries
    'i_op': Operation to broadcast 
    'i_data': Data to check
    'i_addr': Address for write operations
    'o_match': Asserted when 'o_addr' is valid (after a read command)
    'o_addr': Resulting address from a read command

    WARNING: This probably does not handle cases with more than one match?
    """
    def __init__(self, w, sz, init=None):
        self.sz    = sz
        self.width = w
        self.enc   = Encoder(w)

        # One bit wire for each entry
        self.match = Array(Signal() for idx in range(sz))

        # Array of data entries
        if init is not None:
            if len(init) != sz:
                raise Exception("Initial CAM data size mismatch")
            self.data = Array(Signal(w, reset=init[idx]) for idx in range(sz))
        else:
            self.data = Array(Signal(w) for _ in range(sz))

        self.i_en         = Signal()
        self.i_op         = Signal(CAMOp)
        self.i_data       = Signal(w)
        self.i_addr       = Signal(range(sz))
        self.o_match      = Signal()
        self.o_valid      = Signal()
        self.o_addr = Signal(range(sz))

    def ports(self):
        return [ self.i_en, self.i_op, self.i_data, self.i_addr,
                self.o_match, self.o_valid, self.o_addr ]

    def elaborate(self, platform):
        m = Module()

        m.submodules.enc = enc = self.enc
        match = self.match
        data = self.data

        with m.If(self.i_en):
            with m.Switch(self.i_op):
                with m.Case(CAMOp.IDLE):
                    m.d.sync += [ match[i].eq(0) for i in range(self.sz) ]
                with m.Case(CAMOp.READ):
                    m.d.sync += [ match[i].eq(data[i] == self.i_data) 
                                    for i in range(self.sz) ]
                with m.Case(CAMOp.WRITE):
                    m.d.sync += data[self.i_addr].eq(self.i_data)
                    m.d.sync += [ match[i].eq(0) for i in range(self.sz) ]
            m.d.comb += [
                enc.i.eq(Cat(*match)),
                self.o_addr.eq(enc.o),
                self.o_match.eq(~enc.n),
            ]
            m.d.sync += self.o_valid.eq(1)
        with m.Else():
            m.d.comb += [ self.o_match.eq(0), self.o_addr.eq(0) ]
            m.d.sync += self.o_valid.eq(0)

        return m
