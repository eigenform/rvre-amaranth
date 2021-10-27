
from .instruction import *
from ctypes import c_uint32

# Map from base opcodes to different instruction formats
OP_FORMATS = {
    Opcode.OP:       InstFormat.R, 
    Opcode.JAL:      InstFormat.J,
    Opcode.STORE:    InstFormat.S,
    Opcode.BRANCH:   InstFormat.B,
    Opcode.LUI:      InstFormat.U,
    Opcode.AUIPC:    InstFormat.U,
    Opcode.OP_IMM:   InstFormat.I,
    Opcode.LOAD:     InstFormat.I,
    Opcode.MISC_MEM: InstFormat.I,
    Opcode.SYSTEM:   InstFormat.I,
    Opcode.JALR:     InstFormat.I,
} 


class Instr:
    """ Representing a particular RISC-V instruction """
    def __init__(self, op, f3=None, f7=None):
        self.op = op.value
        self.f3 = 0 if f3 == None else f3
        self.f7 = 0 if f7 == None else f7
        self.fmt = OP_FORMATS[op]

# The set of valid RV32I encodings.
RV32I = {
    "lui":   Instr(op=Opcode.LUI,    f3=None,        f7=None),
    "auipc": Instr(op=Opcode.LUI,    f3=None,        f7=None),
    "jal":   Instr(op=Opcode.JAL,    f3=None,        f7=None),
    "jalr":  Instr(op=Opcode.JALR,   f3=None,        f7=None),
    "beq":   Instr(op=Opcode.BRANCH, f3=Funct3.BEQ,  f7=None),
    "bne":   Instr(op=Opcode.BRANCH, f3=Funct3.BNE,  f7=None),
    "blt":   Instr(op=Opcode.BRANCH, f3=Funct3.BLT,  f7=None),
    "bge":   Instr(op=Opcode.BRANCH, f3=Funct3.BGE,  f7=None),
    "bltu":  Instr(op=Opcode.BRANCH, f3=Funct3.BLTU, f7=None),
    "bgeu":  Instr(op=Opcode.BRANCH, f3=Funct3.BGEU, f7=None),
    "lb":    Instr(op=Opcode.LOAD,   f3=Funct3.B,    f7=None),
    "lh":    Instr(op=Opcode.LOAD,   f3=Funct3.H,    f7=None),
    "lw":    Instr(op=Opcode.LOAD,   f3=Funct3.W,    f7=None),
    "lbu":   Instr(op=Opcode.LOAD,   f3=Funct3.BU,   f7=None),
    "lhu":   Instr(op=Opcode.LOAD,   f3=Funct3.HU,   f7=None),
    "sb":    Instr(op=Opcode.STORE,  f3=Funct3.B,    f7=None),
    "sh":    Instr(op=Opcode.STORE,  f3=Funct3.H,    f7=None),
    "sw":    Instr(op=Opcode.STORE,  f3=Funct3.W,    f7=None),
    "addi":  Instr(op=Opcode.OP_IMM, f3=Funct3.ADD,  f7=None),
    "slti":  Instr(op=Opcode.OP_IMM, f3=Funct3.SLT,  f7=None),
    "sltiu": Instr(op=Opcode.OP_IMM, f3=Funct3.SLTU, f7=None),
    "xori":  Instr(op=Opcode.OP_IMM, f3=Funct3.XOR,  f7=None),
    "ori":   Instr(op=Opcode.OP_IMM, f3=Funct3.OR,   f7=None),
    "andi":  Instr(op=Opcode.OP_IMM, f3=Funct3.AND,  f7=None),
    "slli":  Instr(op=Opcode.OP_IMM, f3=Funct3.SLL,  f7=None),
    "srli":  Instr(op=Opcode.OP_IMM, f3=Funct3.SRx,  f7=Funct7.SRL),
    "srai":  Instr(op=Opcode.OP_IMM, f3=Funct3.SRx,  f7=Funct7.SRA),
    "add":   Instr(op=Opcode.OP,     f3=Funct3.ADD,  f7=Funct7.ADD),
    "sub":   Instr(op=Opcode.OP,     f3=Funct3.ADD,  f7=Funct7.SUB),
    "sll":   Instr(op=Opcode.OP,     f3=Funct3.SLL,  f7=None),
    "slt":   Instr(op=Opcode.OP,     f3=Funct3.SLT,  f7=None),
    "sltu":  Instr(op=Opcode.OP,     f3=Funct3.SLTU, f7=None),
    "xor":   Instr(op=Opcode.OP,     f3=Funct3.XOR,  f7=None),
    "srl":   Instr(op=Opcode.OP,     f3=Funct3.SRx,  f7=Funct7.SRL),
    "sra":   Instr(op=Opcode.OP,     f3=Funct3.SRx,  f7=Funct7.SRA),
    "or":    Instr(op=Opcode.OP,     f3=Funct3.XOR,  f7=None),
    "and":   Instr(op=Opcode.OP,     f3=Funct3.XOR,  f7=None),
    # fence  ...
    # ecall  ...
    # ebreak ...
}


def rv32i_asm(s: str):
    """ [Very] naive single-instruction assembler """
    arg = s.replace(",", "").split(" ")
    instr = RV32I.get(arg[0])
    if instr == None:
        raise ValueError("unimplemented/invalid instruction")

    # As far as I'm concerned, the low two bits are always set
    res = 0x00000003
    res |= (instr.op) << 2

    if instr.fmt == InstFormat.R:
        if len(arg) != 4: raise ValueError("Invalid R-type operands")
        rd  = int(arg[1].replace("x", ""))
        rs1 = int(arg[2].replace("x", ""))
        rs2 = int(arg[3].replace("x", ""))

        assert rd < 32 and rs1 < 32 and rs2 < 32

        res |= rd << 7
        res |= instr.f3 << 12
        res |= rs1 << 15
        res |= rs2 << 20
        res |= instr.f7 << 25
        return res

    elif instr.fmt == InstFormat.I:
        if len(arg) != 4: raise ValueError("Invalid I-type operands")
        rd  = int(arg[1].replace("x", ""))
        rs1 = int(arg[2].replace("x", ""))
        imm = int(arg[3], 16)

        assert rd < 32 and rs1 < 32

        imm = c_uint32(imm).value & 0xfff
        res |= rd << 7
        res |= instr.f3 << 12
        res |= rs1 << 15
        res |= imm << 20
        return res

    elif instr.fmt == InstFormat.S:
        if len(arg) != 4: raise ValueError("Invalid S-type operands")
        rs1 = int(arg[1].replace("x", "")) # base
        rs2 = int(arg[2].replace("x", "")) # src (value)
        imm = int(arg[3], 16)

        assert rs1 < 32 and rs2 < 32

        imm = c_uint32(imm).value & 0xfff
        imm_11_5 = (imm & 0b111111100000) >> 5
        imm_4_0  = (imm & 0b000000011111)
        res |= imm_4_0 << 7
        res |= instr.f3 << 12
        res |= rs1 << 15
        res |= rs2 << 20
        res |= imm_11_5 << 25
        return res

    elif instr.fmt == InstFormat.U:
        if len(arg) != 3: raise ValueError("Invalid U-type operands")
        rd  = int(arg[1].replace("x", ""))
        imm = int(arg[2], 16)

        assert rd < 32

        imm = c_uint32(imm).value & 0xfffff
        res |= rd << 7
        res |= imm << 12
        return res

    elif instr.fmt == InstFormat.J:
        if len(arg) != 4: raise ValueError("Invalid J-type operands")
        rd  = int(arg[1].replace("x", ""))
        imm = int(arg[2], 16)

        assert rd < 32

        imm = c_uint32(imm).value & 0xfffff
        imm_20    = (imm & 0b10000000000000000000) >> 19
        imm_19_12 = (imm & 0b01111111100000000000) >> 11
        imm_11    = (imm & 0b00000000010000000000) >> 10
        imm_10_1  = (imm & 0b00000000001111111111)
        res |= rd << 7
        res |= imm_19_12 << 12
        res |= imm_11 << 20
        res |= imm_10_1 << 21
        res |= imm_20 << 31
        return res

    elif instr.fmt == InstFormat.B:
        if len(arg) != 4: raise ValueError("Invalid B-type operands")
        rs1  = int(arg[1].replace("x", ""))
        rs2  = int(arg[2].replace("x", ""))
        imm  = int(arg[3], 16)

        assert rs1 < 32 and rs2 < 32

        imm = c_uint32(imm).value & 0xfff
        imm_12   = (imm & 0b100000000000) >> 11
        imm_11   = (imm & 0b010000000000) >> 10
        imm_10_5 = (imm & 0b001111110000) >> 4
        imm_4_1  = (imm & 0b000000001111)
        res |= imm_11 << 7
        res |= imm_4_1 << 8
        res |= instr.f3 << 12
        res |= rs1 << 15
        res |= rs2 << 20
        res |= imm_10_5 << 25
        res |= imm_12 << 31
        return res


#if __name__ == "__main__":
#    # This makeshift assembler is always "inst [rd], [rs1], [rs2], [imm]"
#    tests = [
#        "lui x1, 0xfffff",
#        "add x1, x2, x3",
#        "sub x1, x2, x3",
#        "lb x2, x1, 0x4",
#        "lh x2, x1, 0x4",
#        "lw x2, x1, 0x4",
#        "sb x1, x2, 0x4",
#        "sh x1, x2, 0x4",
#        "sw x1, x2, 0x4",
#        "addi x1, x2, 0x100",
#        "addi x1, x2, -0x100",
#    ]
#
#    for t in tests:
#        res = rv32i_asm(t)
#        print("{:08x} {}".format(res, t))
#

