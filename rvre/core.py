
from nmigen import *

from .rf import *

class RVRECore(Elaboratable):
    def __init__(self):
        pass
    def elaborate(self, platform):
        m = Module()
        m.domains.sync = ClockDomain()
        return m

