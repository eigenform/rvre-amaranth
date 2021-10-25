
from nmigen import *
from nmigen.sim import *
from nmigen.hdl.rec import *

from instruction import *

class DecoderOutput(Record):
    """ Output control signals from an instruction decoder """
    def __init__(self):
        super().__init__([
            # Instruction operands
            ("rd", 5, DIR_FANOUT), # Output dest. register
            ("rs1", 5, DIR_FANOUT), # Output src. register #1
            ("rs2", 5, DIR_FANOUT), # Output src. register #2
            ("imm", 32, DIR_FANOUT), # Output 32-bit signed immediate

            # Opcode/function control signals
            ("opcd", 5, DIR_FANOUT),
            ("funct3", 3, DIR_FANOUT),
            ("funct7", 7, DIR_FANOUT),

            # Register file write-enable
            #("rf_we", 1, DIR_FANOUT),
        ])

class Decoder(Elaboratable):
    """ Instruction decoder """
    def __init__(self):
        self.out  = DecoderOutput()
        self.inst = Instruction()
        pass
    def elaborate(self, platform):
        m = Module()
        m.d.comb += [
            # Register operands
            self.out.rs1.eq(self.inst.rs1()),
            self.out.rs2.eq(self.inst.rs2()),
            self.out.rd.eq(self.inst.rd()),
            # Opcode/function
            self.out.opcd.eq(self.inst.opcode()),
            self.out.funct3.eq(self.inst.funct3()),
            self.out.funct7.eq(self.inst.funct7()),
        ]
        return m

def test():
    INSTRS = [
        0x00310833, # add x16, x2, x3
        0x005208b3, # add x17, x4, x5
        0x00730933, # add x18, x6, x7
    ]
    def proc():
        for inst in INSTRS:
            yield dut.inst.eq(inst)
            yield Settle()
            rd  = yield dut.out.rd
            rs1 = yield dut.out.rs1
            rs2 = yield dut.out.rs2
            opcd   = yield dut.out.opcd
            funct3 = yield dut.out.funct3
            funct7 = yield dut.out.funct7
            print("rd=x{} rs1=x{} rs2=x{} opcd={} f3={:03b} f7={:07b}".format(
                rd, rs1, rs2, Opcode(opcd).name, funct3, funct7))

    dut = Decoder()
    sim = Simulator(dut)
    sim.add_process(proc)
    sim.run()

if __name__ == "__main__":
    test()


