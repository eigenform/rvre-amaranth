
use rand::Rng;
use rand::distributions::{ Distribution, Standard };

use crate::prim::*;

use crate::unit::*;

#[derive(Debug, Clone, Copy)]
pub enum Width { 
    Byte, 
    Half, 
    Word,
}

#[derive(Debug, Clone, Copy)]
pub enum ALUOp {
    Add,
    Sub,
    Sll,
    Slt,
    Sltu,
    Xor,
    Srl,
    Sra,
    Or,
    And
}
impl ALUOp { 
    pub fn to_uop(&self) -> FunctionalUnitOp {
        match self {
            Self::Add => FunctionalUnitOp::AddSub(AddSubOp::Add),
            Self::Sub => FunctionalUnitOp::AddSub(AddSubOp::Sub),
            Self::Slt => FunctionalUnitOp::Compare(CompareOp::LtSigned),
            Self::Sltu => FunctionalUnitOp::Compare(CompareOp::LtUnsigned),
            Self::Xor => FunctionalUnitOp::Logical(LogicalOp::Xor),
            Self::And => FunctionalUnitOp::Logical(LogicalOp::And),
            Self::Or => FunctionalUnitOp::Logical(LogicalOp::Or),
            Self::Sll => FunctionalUnitOp::Logical(LogicalOp::Sll),
            Self::Srl => FunctionalUnitOp::Logical(LogicalOp::Srl),
            Self::Sra => FunctionalUnitOp::Logical(LogicalOp::Sra),
        }
    }
}

pub enum Immediate {
    U32(u32),
    S32(i32),
}

#[derive(Debug, Clone, Copy)]
pub struct OperandList {
    pub rs1: Option<ArchReg>,
    pub rs2: Option<ArchReg>,
}
impl OperandList {
}


#[derive(Debug, Clone, Copy)]
pub enum Opcode {
    /// ALU operation
    Op(ArchReg, ArchReg, ArchReg, ALUOp),
    /// ALU operation with immediate
    OpImm(ArchReg, ArchReg, i32, ALUOp),
    /// Load upper immediate
    Lui(ArchReg, u32),
    /// Memory load
    Load(ArchReg, ArchReg, i32, Width),
    /// Memory store
    Store(ArchReg, ArchReg, i32, Width),
}

impl Opcode {
    pub fn reg_operands(&self) -> OperandList {
        match *self {
            Self::Op(_, rs1, rs2, _) => 
                OperandList { rs1: Some(rs1), rs2: Some(rs2) },
            Self::OpImm(_, rs1, _, _) => 
                OperandList { rs1: Some(rs1), rs2: None },
            Self::Lui(_, _) => 
                OperandList { rs1: None, rs2: None },
            Self::Load(_, rs1, _, _) => 
                OperandList { rs1: Some(rs1), rs2: None },
            Self::Store(rs1, rs2, _, _) => 
                OperandList { rs1: Some(rs1), rs2: Some(rs2) },
        }
    }
    pub fn is_store(&self) -> bool {
        matches!(self, Opcode::Store(_, _, _, _))
    }
}


impl Distribution<Width> for Standard {
    fn sample<R: Rng + ?Sized>(&self, rng: &mut R) -> Width {
         match rng.gen_range(0..=2) {
             0 => Width::Byte,
             1 => Width::Half,
             _ => Width::Word,
         }
    }
}

impl Distribution<ALUOp> for Standard {
    fn sample<R: Rng + ?Sized>(&self, rng: &mut R) -> ALUOp {
         match rng.gen_range(0..=9) {
             0 => ALUOp::Add,
             1 => ALUOp::Sub,
             2 => ALUOp::Sll,
             3 => ALUOp::Slt,
             4 => ALUOp::Sltu,
             5 => ALUOp::Xor,
             6 => ALUOp::Srl,
             7 => ALUOp::Sra,
             8 => ALUOp::Or,
             _ => ALUOp::And,
         }
    }
}

impl Distribution<Opcode> for Standard {
    fn sample<R: Rng + ?Sized>(&self, rng: &mut R) -> Opcode {
        let rd  = ArchReg(rng.gen_range(1..=7));
        let rs1 = ArchReg(rng.gen_range(0..=7));
        let rs2 = ArchReg(rng.gen_range(0..=7));

        let mut op: ALUOp = rng.gen();

        // TODO: Fix after you implement signed immediates
        if matches!(op, ALUOp::Slt) {
            op = ALUOp::Sltu;
        }

        match rng.gen_range(0..2) {
            0 => {
                let imm = match op {
                    // shamt is 5-bits
                    ALUOp::Sll | ALUOp::Srl | ALUOp::Sra => {
                        rng.gen_range(0..32)
                    },
                    // otherwise, 12-bit signed integer
                    _ => rng.gen_range(-0xfff..=0xfff)
                };
                // SUB isn't valid for OpImm instructions
                if matches!(op, ALUOp::Sub) {
                    op = ALUOp::Add;
                }
                Opcode::OpImm(rd, rs1, imm, op)
            },
            _ => Opcode::Op(rd, rs1, rs2, op),
            //_ => Opcode::Lui(rd, rng.gen_range(0x0000_0000..=0x000f_ffff)),
        }
    }
}

