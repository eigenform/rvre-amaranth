//! Describing different types of execution units.

use std::ops::{ BitOr, BitXor, BitAnd, Shr, Shl };
use crate::sched::*;

/// Operations for an [AddSubUnit].
#[derive(Debug, Copy, Clone)]
pub enum AddSubOp { Add, Sub }

/// Operations for a [LogicalOpUnit].
#[derive(Debug, Copy, Clone)]
pub enum LogicalOp { And, Or, Xor, Sll, Srl, Sra }

/// Operations for a [ComparatorUnit].
#[derive(Debug, Copy, Clone)]
pub enum CompareOp { LtSigned, LtUnsigned }

/// Operations corresponding to different functional units.
#[derive(Debug, Copy, Clone)]
pub enum FunctionalUnitOp {
    AddSub(AddSubOp),
    Logical(LogicalOp),
    Compare(CompareOp),
}


/// Common interface for an execution unit.
pub trait FunctionalUnit {
    fn new() -> Self;

    /// Send some operation to this unit.
    fn prepare(&mut self, op: DispatchedOp);
    /// Perform the current operation, producing a result.
    fn execute(&mut self);
    /// Return the operation and result data, clearing the unit's state.
    fn complete(&mut self) -> Option<u32>;
}

pub struct AddSubUnit {
    pending: Option<DispatchedOp>,
    result: Option<u32>,
}
impl FunctionalUnit for AddSubUnit {
    fn new() -> Self { 
        Self { pending: None, result: None } 
    }
    fn prepare(&mut self, op: DispatchedOp) {
        *self = Self { pending: Some(op), result: None };
    }
    fn execute(&mut self) {
        if let Some(ifo) = self.pending {
            let res = match ifo.uop {
                FunctionalUnitOp::AddSub(op) => match op {
                    AddSubOp::Add => ifo.x.wrapping_add(ifo.y),
                    AddSubOp::Sub => ifo.x.wrapping_sub(ifo.y),
                },
                _ => unimplemented!(),
            };
            self.result = Some(res);
            println!("[execute] ASU completed with {:08x}", res);
        } else {
            println!("[execute] ASU was empty");
        }
    }
    fn complete(&mut self) -> Option<u32> {
        let res = self.result.take();
        self.pending = None;
        res
    }
}

pub struct LogicalOpUnit {
    pending: Option<DispatchedOp>,
    result: Option<u32>,
}
impl FunctionalUnit for LogicalOpUnit {
    fn new() -> Self { 
        Self { pending: None, result: None } 
    }
    fn prepare(&mut self, op: DispatchedOp) {
        *self = Self { pending: Some(op), result: None };
    }
    fn execute(&mut self) {
        if let Some(ifo) = self.pending {
            let res = match ifo.uop {
                FunctionalUnitOp::Logical(op) => match op {
                    LogicalOp::Xor => ifo.x.bitxor(ifo.y),
                    LogicalOp::Or  => ifo.x.bitor(ifo.y),
                    LogicalOp::And => ifo.x.bitand(ifo.y),
                    LogicalOp::Sll => ifo.x.shl(ifo.y),
                    LogicalOp::Srl => ifo.x.shr(ifo.y),
                    LogicalOp::Sra => (ifo.x as i32).shr(ifo.y as i32) as u32,
                },
                _ => unimplemented!(),
            };
            self.result = Some(res);
            println!("[execute] LOU completed with {:08x}", res);
        } else {
            println!("[execute] LOU was empty");
        }
    }
    fn complete(&mut self) -> Option<u32> {
        let res = self.result.take();
        self.pending = None;
        res
    }

}

pub struct ComparatorUnit {
    pending: Option<DispatchedOp>,
    result: Option<u32>,
}
impl FunctionalUnit for ComparatorUnit {
    fn new() -> Self { 
        Self { pending: None, result: None } 
    }
    fn prepare(&mut self, op: DispatchedOp) {
        *self = Self { pending: Some(op), result: None };
    }
    fn execute(&mut self) {
        if let Some(ifo) = self.pending {
            let res = match ifo.uop {
                FunctionalUnitOp::Compare(op) => match op {
                    CompareOp::LtSigned  => {
                        if (ifo.x as i32) < (ifo.y as i32) { 1 } else { 0 }
                    },
                    CompareOp::LtUnsigned => {
                        if ifo.x < ifo.y { 1 } else { 0 }
                    },
                },
                _ => unimplemented!(),
            };
            self.result = Some(res);
            println!("[execute] CRU completed with {:08x}", res);
        } else {
            println!("[execute] CRU was empty");
        }
    }
    fn complete(&mut self) -> Option<u32> {
        let res = self.result.take();
        self.pending = None;
        res
    }

}
