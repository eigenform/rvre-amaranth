
from instruction import *

class Field:
    """ Describes a bitfield within some instruction encoding """
    def __init__(self, pos: int, length: int):
        self.pos = pos
        self.len = length
        self.mask = 0x00000000
        self.mask |= ((1 << length) - 1) << pos
    def gen(self, val: int): 
        return (val << self.pos) & self.mask

# Map from instruction formats to sets of relevant bitfields
FIELDS = {
    InstFormat.R: { 
        "op": Field(2, 5), "rd": Field(7, 5), "f3": Field(12,3), 
        "rs1": Field(15, 5), "rs2": Field(20, 5), "f7": Field(25, 7),
    },
    InstFormat.I: { 
        "op": Field(2, 5), "rd": Field(7, 5), "f3": Field(12, 3), 
        "rs1": Field(15, 5), "imm12": Field(20, 12), 
    },
    InstFormat.S: { 
        "op": Field(2,5), "imm_4_0": Field(7,5), "f3": Field(12,3), 
        "rs1": Field(15,5), "rs2": Field(20,5), "imm_11_5": Field(25,7),
    },
    InstFormat.B: { 
        "op": Field(2,5), "imm_11": Field(7,1), "imm_4_1": Field(8,4), 
        "f3": Field(12,3), "rs1": Field(15,5), "rs2": Field(20,5), 
        "imm_10_5": Field(25,6), "imm_12": Field(31,1),
    },
    InstFormat.U: { 
        "op": Field(2,5), "rd": Field(7,5), "imm20": Field(12,20), 
    },
    InstFormat.J: { 
        "op": Field(2,5), "rd": Field(7,5), "imm_19_12": Field(12,8), 
        "imm_11": Field(20,1), "imm_10_1": Field(21,10), 
        "imm_20": Field(31,1),
    },
}

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
        self.op = op
        self.f3 = f3
        self.f7 = f7
        self.fmt = OP_FORMATS[op]

    def encode(self, **kwargs):
        """ Encode this instruction into a 32-bit unsigned integer """
        res = 0x00000003
        fields = FIELDS[self.fmt]
        for (k, v) in kwargs.items():
            if k in fields:
                res |= fields[k].gen(v)
                print(k, v)
        for name in fields:
            field = fields[name]
            if name == "op":   res |= field.gen(self.op.value)
            elif name == "f3": res |= field.gen(self.f3)
            elif name == "f7": res |= field.gen(self.f7)
            print(name, field)
        print("{:08x}".format(res))


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

def gen_i_imm12(x: int) -> int:
    if (x >= 0x800) or (x <= -0x800):
        raise ValueError("Can't represent 0x{:0x} as 12-bit signed integer")
    if x < 0:
        res = (0b011111111111 & abs(x)) | 0b100000000000
    else:
        res = (0b011111111111 & x)
    return res << 20

def gen_s_imm12(x: int) -> int:
    if (x >= 0x800) or (x <= -0x800):
        raise ValueError("Can't represent 0x{:0x} as 12-bit signed integer")
    if x < 0:
        res = (0b011111111111 & abs(x)) | 0b100000000000
    else:
        res = (0b011111111111 & x)
    lo = (res & 0b000000011111) << 7
    hi = (res & 0b111111100000) << 20
    return (lo | hi)

def gen_u_imm20(x: int) -> int:
    if (x < 0) or (x > 0xfffff):
        raise ValueError("Can't represent 0x{:0x} as 20-bit unsigned integer")
    return (x & 0xfffff) << 12 


print("i {:032b}".format(gen_i_imm12(0x7ff)))
print("i {:032b}".format(gen_i_imm12(-0x7ff)))
print("s {:032b}".format(gen_s_imm12(0x7ff)))
print("s {:032b}".format(gen_s_imm12(-0x7ff)))
print("u {:032b}".format(gen_u_imm20(0xfffff)))

def rv32i_asm(s: str):
    """ Naive single-instruction assembler """
    arg = s.replace(",", "").split(" ")
    instr = RV32I.get(arg[0])
    if instr == None:
        raise ValueError("unimplemented/invalid instruction")

    if instr.fmt == InstFormat.R:
        if len(arg) != 4: raise ValueError("Invalid R-type operands")
        rd  = int(arg[1].replace("x", ""))
        rs1 = int(arg[2].replace("x", ""))
        rs2 = int(arg[3].replace("x", ""))
    elif instr.fmt == InstFormat.I:
        if len(arg) != 4: raise ValueError("Invalid I-type operands")
        rd  = int(arg[1].replace("x", ""))
        rs1 = int(arg[2].replace("x", ""))
        imm = int(arg[3], 16)
    elif instr.fmt == InstFormat.S:
        if len(arg) != 4: raise ValueError("Invalid S-type operands")
        rs1_base = int(arg[1].replace("x", ""))
        rs2_src  = int(arg[2].replace("x", ""))
        imm      = int(arg[3], 16)
    elif instr.fmt == InstFormat.U:
        if len(arg) != 3: raise ValueError("Invalid U-type operands")
        rd  = int(arg[1].replace("x", ""))
        imm = int(arg[2], 16)
    elif instr.fmt == InstFormat.J:
        if len(arg) != 4: raise ValueError("Invalid J-type operands")
        rd  = int(arg[1].replace("x", ""))
        imm = int(arg[2], 16)

if __name__ == "__main__":
    rv32i_asm("lui x1, 0xfffff")
    rv32i_asm("add x1, x2, x3")
    rv32i_asm("sw x1, x2, 0x4")
    rv32i_asm("lw x1, x2, 0x4")



