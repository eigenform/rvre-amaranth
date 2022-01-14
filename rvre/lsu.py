from enum import Enum, unique

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
