
from nmigen import *
from nmigen.hdl.rec import *
from nmigen.sim import *


class RFInterface(Record):
    def __init__(self):
        super().__init__([
            # Register write enable/index/data
            ("rd_we", 1, DIR_FANIN),
            ("rd", 5, DIR_FANIN), 
            ("rd_data", 32, DIR_FANIN),
            # Register read index/data
            ("rs1", 5, DIR_FANIN), ("rs1_data", 32, DIR_FANOUT),
            ("rs2", 5, DIR_FANIN), ("rs2_data", 32, DIR_FANOUT),
        ])

class RegisterFile(Elaboratable):
    """ Architectural register file. 
    """
    def __init__(self, init_data: list[int]=[]):
        self.interface = RFInterface()
        self.mem = Memory(width=32, depth=32, init=init_data)
    def elaborate(self, platform):
        m = Module()

        # Synchronous write port
        m.submodules.wp1 = wp1 = self.mem.write_port()
        # Asynchronous read ports
        m.submodules.rp1 = rp1 = self.mem.read_port(domain='comb')
        m.submodules.rp2 = rp2 = self.mem.read_port(domain='comb')

        # Handle register writes (and disable writes to x0)
        m.d.comb += [
            wp1.en.eq(Mux(self.interface.rd == 0, 0, self.interface.rd_we)),
            wp1.addr.eq(self.interface.rd),
            wp1.data.eq(self.interface.rd_data),
        ]

        # Handle register reads
        m.d.comb += [
            rp1.addr.eq(self.interface.rs1),
            rp2.addr.eq(self.interface.rs2),
            self.interface.rs1_data.eq(rp1.data),
            self.interface.rs2_data.eq(rp2.data),
        ]

        return m


def test():
    def rw_all():
        for ridx in range(0,32):
            yield dut.interface.rd.eq(ridx)
            yield dut.interface.rd_data.eq(ridx << 24)
            yield dut.interface.rd_we.eq(1)
            yield dut.interface.rs1.eq(ridx)
            yield dut.interface.rs2.eq(ridx)
            yield Tick()
            yield Settle()
            rs1_d = yield dut.interface.rs1_data
            rs2_d = yield dut.interface.rs2_data
            assert rs1_d == rs2_d == (ridx << 24)

    def write_x0():
        yield dut.interface.rd.eq(0)
        yield dut.interface.rd_data.eq(0xdeadbeef)
        yield dut.interface.rd_we.eq(1)
        yield dut.interface.rs1.eq(0)
        yield dut.interface.rs2.eq(0)
        yield Tick()
        yield Settle()
        rs1_d = yield dut.interface.rs1_data
        rs2_d = yield dut.interface.rs2_data
        assert rs1_d == rs2_d == 0

    def read_x0():
        yield dut.interface.rd_we.eq(0)
        yield dut.interface.rs1.eq(0)
        yield dut.interface.rs2.eq(0)
        yield Tick()
        yield Settle()
        rs1_d = yield dut.interface.rs1_data
        rs2_d = yield dut.interface.rs2_data
        assert rs1_d == rs2_d == 0

    dut = RegisterFile()
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(rw_all)
    sim.add_sync_process(write_x0)
    sim.add_sync_process(read_x0)
    sim.run()

if __name__ == "__main__":
    test()

