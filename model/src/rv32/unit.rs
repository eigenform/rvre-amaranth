
//use std::ops::{ BitOr, BitXor, BitAnd, Shr, Shl };
//use crate::rv32::isa::*;
//
//
///// Execution unit for add/subtract operations.
//pub struct AddSubUnit {
//    op: Option<ALUOp>,
//    x: Option<u32>,
//    y: Option<u32>,
//    res: Option<u32>,
//    done: bool,
//}
//impl AddSubUnit {
//    pub fn new() -> Self {
//        Self {
//            op: None, x: None, y: None, res: None, done: false
//        }
//    }
//    pub fn prepare(&mut self, op: ALUOp, x: u32, y: u32) {
//        self.op = Some(op);
//        self.x = Some(x);
//        self.y = Some(y);
//        self.res = None;
//        self.done = false;
//    }
//
//    pub fn execute(&self) {
//        let res = match self.op {
//            ALUOp::Add => self.x.wrapping_add(self.y),
//            ALUOp::Sub => self.x.wrapping_sub(self.y),
//            _ => unimplemented!(),
//        };
//        self.res = Some(res);
//        self.done = true;
//    }
//}
//
///// Execution unit for bitwise logical operations.
//pub struct LogicalOpUnit {
//    op: ALUOp,
//    x: u32,
//    y: u32,
//    res: Option<u32>,
//    done: bool,
//}
//impl LogicalOpUnit {
//    pub fn prepare(&mut self, op: ALUOp, x: u32, y: u32) {
//        self.op = op;
//        self.x = x;
//        self.y = y;
//        self.res = None;
//        self.done = false;
//    }
//
//    pub fn execute(&self) {
//        let res = match self.op {
//            ALUOp::Xor => self.x.bitxor(self.y),
//            ALUOp::Or  => self.x.bitor(self.y),
//            ALUOp::And => self.x.bitand(self.y),
//            ALUOp::Sll => self.x.shl(self.y),
//            ALUOp::Srl => self.x.shr(self.y),
//            ALUOp::Sra => (self.x as i32).shr(self.y as i32) as u32,
//            _ => unimplemented!(),
//        };
//        self.res = Some(res);
//        self.done = true;
//    }
//}
//
//pub struct ComparatorUnit {
//    op: ALUOp,
//    x: u32,
//    y: u32,
//    res: Option<u32>,
//    done: bool,
//}
//impl ComparatorUnit {
//    pub fn prepare(&mut self, op: ALUOp, x: u32, y: u32) {
//        self.op = op;
//        self.x = x;
//        self.y = y;
//        self.res = None;
//        self.done = false;
//    }
//
//    pub fn execute(&self) {
//        let res = match self.op {
//            ALUOp::Slt  => {
//                if (self.x as i32) < (self.y as i32) { 1 } else { 0 }
//            },
//            ALUOp::Sltu => if self.x < self.y { 1 } else { 0 },
//            _ => unimplemented!(),
//        };
//        self.res = Some(res);
//        self.done = true;
//    }
//}


