
from amaranth import *
from amaranth.hdl.rec import *
from amaranth.lib.fifo import *

class IssueQueueEntry(Layout):
    def __init__(self):
        super().__init__([
        ])

class IssueQueue(Elaboratable):
    def __init__(self, depth):
        self.depth = depth
        self.data  = SyncFIFO(width=IssueQueueEntry, depth=4)
    def elaborate(self, platform):
        m = Module()
        return m
