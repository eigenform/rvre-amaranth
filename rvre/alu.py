""" alu.py
ALU logic.
"""

from amaranth import *
from amaranth.sim import *
from enum import Enum, unique

from .common import ALUOp

class ALU(Elaboratable):
    """ Arithmetic/logic unit """
    def __init__(self):
        self.i_op     = Signal(ALUOp)
        self.i_x      = Signal(32)
        self.i_y      = Signal(32)
        self.o_res    = Signal(32)

    def ports(self):
        return [ self.i_op, self.i_x, self.i_y, self.o_res ]

    def elaborate(self, platform):
        m = Module()

        shamt = Signal(5)
        m.d.comb += shamt.eq(self.i_y[0:5])

        with m.Switch(self.i_op):
            with m.Case(ALUOp.ADD): 
                m.d.comb += self.o_res.eq(self.i_x + self.i_y)
            with m.Case(ALUOp.SUB): 
                m.d.comb += self.o_res.eq(self.i_x - self.i_y)
            with m.Case(ALUOp.SLL): 
                m.d.comb += self.o_res.eq(self.i_x << shamt)
            with m.Case(ALUOp.SLT): 
                m.d.comb += self.o_res.eq(self.i_x < self.i_y)
            with m.Case(ALUOp.XOR): 
                m.d.comb += self.o_res.eq(self.i_x ^ self.i_y)
            with m.Case(ALUOp.SRA): 
                m.d.comb += self.o_res.eq(self.i_x >> shamt)
            with m.Case(ALUOp.OR): 
                m.d.comb += self.o_res.eq(self.i_x | self.i_y)
            with m.Case(ALUOp.AND): 
                m.d.comb += self.o_res.eq(self.i_x & self.i_y)
        return m


