from enum import Enum, unique

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

