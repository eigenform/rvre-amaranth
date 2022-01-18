
from amaranth import *
from amaranth.hdl.rec import *
from amaranth.lib.fifo import *

from .common import *

class IssueQueueEntry(Layout):
    def __init__(self):
        super().__init__([
            ("alu_op", ALUOp), 
            ("lsu_op", LSUOp), 
            ("bru_op", BRUOp), 
            ("rd", ArchReg),
            ("prd", PhysReg),
            ("prs1", PhysReg),
            ("prs2", PhysReg),
        ])

class IssueUnit(Elaboratable):
    def __init__(self, queue_size):
        self.queue_size = queue_size
        self.q = Array(Record(IssueQueueEntry) for _ in range(queue_size))

    def elaborate(self, platform):
        m = Module()

        #for i in queue_size:

        return m

class IssueQueue(Elaboratable):
    """ In-order issue queue.
    """
    def __init__(self, depth):
        self.depth = depth
        self.queue = SyncFIFO(width=IssueQueueEntry, depth=4)
        self.i_wdata = Record(IssueQueueEntry)
        self.i_wen   = Signal()
        self.i_ren   = Signal()
        self.o_wrdy  = Signal()
        self.o_rrdy  = Signal()
        self.o_data  = Record(IssueQueueEntry)

    def elaborate(self, platform):
        m = Module()
        m.submodules.q = q = self.queue
        m.d.comb += [
            q.w_en.eq(self.i_wen),
            self.o_wrdy.eq(q.w_rdy),
            q.w_data.eq(self.i_wdata),
            q.r_en.eq(self.i_ren),
            self.o_rrdy.eq(q.r_rdy),
            self.o_data.eq(q.r_data),
        ]

        return m


