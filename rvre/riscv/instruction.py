
from amaranth import *
from enum import Enum

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

class InstFormat(Enum):
    """ Constants for each RISC-V instruction format. """
    R = 0 # rd, rs1, rs2
    I = 1 # rd, rs1, imm
    S = 2 # rs1, rs2, imm
    B = 3 # rs1, rs2, imm
    U = 4 # rd, imm
    J = 5 # rd, imm

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


