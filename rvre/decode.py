
from functools import reduce
from itertools import starmap
from operator import or_

from amaranth import *
from amaranth.sim import *
from amaranth.hdl.rec import *

from .common import *

FMT_RD  = (InstFormat.R, InstFormat.I, InstFormat.U, InstFormat.J)
FMT_RS1 = (InstFormat.R, InstFormat.I, InstFormat.S, InstFormat.B)
FMT_RS2 = (InstFormat.R, InstFormat.S, InstFormat.B)


class DecodeUnit(Elaboratable):
    """ Instruction decoder unit.
    Decompose a 32-bit instruction into some set of control signals.
    """
    def __init__(self):
        self.i_inst    = Instruction()
        self.o_illegal = Signal()
        self.o_op      = Signal(Opcode)
        self.o_alu_op  = Signal(ALUOp)
        self.o_lsu_op  = Signal(LSUOp)
        self.o_bru_op  = Signal(BRUOp)
        self.o_ifmt    = Signal(InstFormat)
        self.o_rd      = Signal(ArchReg)
        self.o_rs1     = Signal(ArchReg)
        self.o_rs2     = Signal(ArchReg)
        self.o_rd_en   = Signal()
        self.o_rs1_en  = Signal()
        self.o_rs2_en  = Signal()
        self.o_imm     = Signal(32)

    def ports(self):
        return [ 
            self.i_inst,
            self.o_illegal,
            self.o_op,
            self.o_alu_op,
            self.o_lsu_op,
            self.o_bru_op,
            self.o_ifmt,
            self.o_rd,
            self.o_rs1,
            self.o_rs2,
            self.o_rd_en,
            self.o_rs1_en,
            self.o_rs2_en,
            self.o_imm
        ]

    def elaborate(self, platform):
        m = Module()

        op = Signal(Opcode)
        ifmt = Signal(InstFormat)
        f3 = Signal(3)
        f7 = Signal(7)
        st_op = Signal()

        m.d.comb += [
            op.eq(self.i_inst.op()),
            f3.eq(self.i_inst.f3()),
            f7.eq(self.i_inst.f7()),
            st_op.eq(op == Opcode.STORE),
        ]

        with m.Switch(op):
            with m.Case(Opcode.LOAD):
                m.d.comb += [ 
                    ifmt.eq(InstFormat.I),
                    self.o_alu_op.eq(ALUOp.ADD) 
                ]
            with m.Case(Opcode.OP_IMM):
                m.d.comb += [ 
                    ifmt.eq(InstFormat.I),
                    self.o_alu_op.eq(Cat(f3, f7[1]))
                ]
            with m.Case(Opcode.AUIPC):
                m.d.comb += [ 
                    ifmt.eq(InstFormat.U),
                    self.o_alu_op.eq(ALUOp.ADD) 
                ]
            with m.Case(Opcode.STORE):
                m.d.comb += [ 
                    ifmt.eq(InstFormat.S),
                    self.o_alu_op.eq(ALUOp.ADD)
                ]
            with m.Case(Opcode.OP):
                m.d.comb += [ 
                    ifmt.eq(InstFormat.R),
                    self.o_alu_op.eq(Cat(f3, f7[1]))
                ]
            with m.Case(Opcode.LUI):
                m.d.comb += [ 
                    ifmt.eq(InstFormat.U),
                    self.o_alu_op.eq(ALUOp.ADD)
                ]
            with m.Case(Opcode.BRANCH):
                m.d.comb += [ 
                    ifmt.eq(InstFormat.B),
                    #self.o_alu_op.eq(Cat(f3, f7[1]))
                ]
            with m.Case(Opcode.JALR):
                m.d.comb += [ 
                    ifmt.eq(InstFormat.I),
                    self.o_alu_op.eq(ALUOp.ADD),
                ]
            with m.Case(Opcode.JAL):
                m.d.comb += [ 
                    ifmt.eq(InstFormat.J),
                    self.o_alu_op.eq(ALUOp.ADD),
                ]
            with m.Default():
                m.d.comb += [ 
                    self.o_illegal.eq(1)
                ]

        with m.Switch(ifmt):
            with m.Case(InstFormat.I):
                m.d.comb += self.o_imm.eq(self.i_inst.i_simm12())
            with m.Case(InstFormat.S):
                m.d.comb += self.o_imm.eq(self.i_inst.s_simm12())
            with m.Case(InstFormat.B):
                m.d.comb += self.o_imm.eq(self.i_inst.b_simm12())
            with m.Case(InstFormat.U):
                m.d.comb += self.o_imm.eq(self.i_inst.u_imm20())
            with m.Case(InstFormat.J):
                m.d.comb += self.o_imm.eq(self.i_inst.j_simm20())

        m.d.comb += [
            self.o_op.eq(op),
            self.o_ifmt.eq(ifmt),
            self.o_lsu_op.eq( Cat(st_op, f3) ),
            self.o_bru_op.eq(f3),
            self.o_illegal.eq(self.i_inst[0:2] != 0b11),
            self.o_rd.eq( self.i_inst.rd()),
            self.o_rs1.eq(self.i_inst.rs1()),
            self.o_rs2.eq(self.i_inst.rs2()),

            self.o_rd_en.eq( reduce(or_, (ifmt == F for F in FMT_RD))),
            self.o_rs1_en.eq(reduce(or_, (ifmt == F for F in FMT_RS1))),
            self.o_rs2_en.eq(reduce(or_, (ifmt == F for F in FMT_RS2))),
        ]

        return m

