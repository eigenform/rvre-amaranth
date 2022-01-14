""" Declares constants and common signal types used in the machine.
"""

from math import ceil, log2
from enum import Enum, unique

from amaranth import *
from amaranth.hdl.rec import *

from .param import *

__all__ = [
    "Instruction",
    "InstFormat", "Opcode", "Funct3", "Funct7",

    "ALUOp", "LSUOp", "BRUOp",
    "PhysReg", "ArchReg", 
    "Uop",
]

class Instruction(Signal):
    """ Wrapper for easily slicing a 32-bit RISC-V instruction. """
    def __init__(self):
        super().__init__(shape=unsigned(32))

    def op(self): return self[2:7]
    def f3(self): return self[12:15]
    def f7(self): return self[25:32]

    def rd(self):  return self[7:12]
    def rs1(self): return self[15:20]
    def rs2(self): return self[20:25]

    def i_simm12(self): 
        return Cat(self[20:], Repl(self[-1], 20))
    def u_imm20(self):
        return Cat(C(0, 12), self[12:])
    def s_simm12(self): 
        return Cat(self[7:12], self[25:], Repl(self[-1], 20))
    def b_simm12(self): 
        return Cat(C(0, 1), self[8:12], self[25:31], self[7], Repl(self[-1], 20))
    def j_simm20(self): 
        return Cat(C(0, 1), self[21:31], self[20], self[12:20], Repl(self[-1], 12))

@unique
class InstFormat(Enum):
    """ Constant identifier for each RISC-V instruction format. """
    R = 0 # rd, rs1, rs2
    I = 1 # rd, rs1, imm
    S = 2 # rs1, rs2, imm
    B = 3 # rs1, rs2, imm
    U = 4 # rd, imm
    J = 5 # rd, imm

@unique
class Opcode(Enum):
    """ RISC-V base opcode map """
    LOAD        = 0b00000 # [lb, lh, lw, lbu, lhu]
    #LOAD_FP    = 0b00001 
    #CUSTOM_0   = 0b00010 
    MISC_MEM    = 0b00011 # [fence, fence.i]
    OP_IMM      = 0b00100 # [addi, slti, sltiu, xori, ori, andi]
    AUIPC       = 0b00101 
    #OP_IMM_32  = 0b00110
    STORE       = 0b01000 # [sb, sh, sw]
    #STORE_FP   = 0b01001
    #CUSTOM_1   = 0b01010
    #AMO        = 0b01011
    OP          = 0b01100 # [add, sub, sll, slt, sltu, xor, srl, sra, or, and]
    LUI         = 0b01101
    #OP_32      = 0b01110
    #MADD       = 0b10000
    #MSUB       = 0b10001
    #NMSUB      = 0b10010
    #NMADD      = 0b10011
    #OP_FP      = 0b10100 
    #RES        = 0b10101
    #CUSTOM_2   = 0b10110
    BRANCH      = 0b11000 # [beq, bne, blt, bge, bltu, bgeu]
    JALR        = 0b11001
    #RES        = 0b11010
    JAL         = 0b11011
    SYSTEM      = 0b11100
    #RES        = 0b11101
    #CUSTOM_3   = 0b11110

class Funct3:
    """ Mappings to 'funct3' field values """
    BEQ  = B  = ADD  = 0b000
    BNE  = H  = SLL  = 0b001
    _    = W  = SLT  = 0b010
    _    = _  = SLTU = 0b011
    BLT  = BU = XOR  = 0b100
    BGE  = HU = SRx  = 0b101
    BLTU = _  = OR   = 0b110
    BGEU = _  = AND  = 0b111

class Funct7:
    """ Mappings to 'funct7' field values """
    ADD = SRL = 0b0000000
    SUB = SRA = 0b0100000


@unique
class ALUOp(Enum):
    """ Constant identifier for an ALU operation.
    Formed by taking 'Cat( Funct3, Funct7[1] )'.
    """
    ADD  = 0b0000
    SUB  = 0b0001
    SLL  = 0b0010
    SLT  = 0b0100
    SLTU = 0b0110
    XOR  = 0b1000
    SRL  = 0b1010
    SRA  = 0b1011
    OR   = 0b1100
    AND  = 0b1110

@unique
class LSUOp(Enum):
    """ Constant identifier for an LSU operation.
    Formed by taking 'Cat( Funct3, (Opcode == Opcode.STORE) )'.
    """
    LD_B  = 0b0000
    LD_H  = 0b0010
    LD_W  = 0b0100
    LD_BU = 0b1000
    LD_HU = 0b1010
    ST_B  = 0b0001
    ST_H  = 0b0011
    ST_W  = 0b0101

@unique
class BRUOp(Enum):
    """ Constant identifier for a particular BRU operation.
    Corresponds directly to the 'funct3' field.
    """
    BEQ  = 0b000
    BNE  = 0b001
    ILL2 = 0b010
    ILL3 = 0b011
    BLT  = 0b100
    BGE  = 0b101
    BLTU = 0b110
    BGEU = 0b111

class PhysReg(Shape):
    """ The shape of a physical register index. """
    def __init__(self, **kwargs):
        super().__init__(width=PARAM.prf_size, *kwargs)

class ArchReg(Shape):
    """ The shape of an architectural register index. """
    def __init__(self, **kwargs):
        super().__init__(width=ceil(log2(32)), *kwargs)

class Uop(Layout):
    """ Internal representation of an instruction (post-rename).
    """
    def __init__(self):
        super().__init__([
            ('rd',     ArchReg),
            ('prd',    PhysReg), 
            ('ps1',    PhysReg), 
            ('ps2',    PhysReg),
            ('alu_op', ALUOp), 
            ('lsu_op', LSUOp),
            ('bru_op', BRUOp),
        ])


