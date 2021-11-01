//! Describing different types of execution units.

use std::ops::{ BitOr, BitXor, BitAnd, Shr, Shl };
use crate::sched::*;
use crate::rob::*;

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


#[derive(Debug, Copy, Clone)]
pub struct CompletedOp {
    pub rob_idx: usize,
    pub res: u32,
}


/// Common interface for an execution unit (EU).
pub trait ExecutionUnit {
    fn new() -> Self;
    fn is_busy(&self) -> bool;
    /// Send some operation to this unit.
    fn prepare(&mut self, op: &DispatchedOp);
    /// Perform the current operation, producing a result.
    fn execute(&mut self);
    /// Return the operation and result data, clearing the unit's state.
    fn complete(&mut self) -> Option<DispatchedOp>;
}

pub struct AddSubUnit {
    pending: Option<DispatchedOp>,
}
impl ExecutionUnit for AddSubUnit {
    fn new() -> Self { Self { pending: None } }
    fn is_busy(&self) -> bool { self.pending.is_some() }
    fn prepare(&mut self, op: &DispatchedOp) {
        *self = Self { pending: Some(op.clone()) }
    }
    fn execute(&mut self) {
        if let Some(ref mut ifo) = self.pending {
            let res = match ifo.uop {
                FunctionalUnitOp::AddSub(op) => match op {
                    AddSubOp::Add => ifo.x.wrapping_add(ifo.y),
                    AddSubOp::Sub => ifo.x.wrapping_sub(ifo.y),
                },
                _ => unimplemented!(),
            };
            ifo.res = Some(res);
            println!("[execute] ASU completed with {:08x}", res);
        } else {
            println!("[execute] ASU was empty");
        }
    }
    fn complete(&mut self) -> Option<DispatchedOp> {
        match &self.pending {
            None => None,
            Some(op) => {
                if op.res.is_some() {
                    self.pending.take()
                } else {
                    None
                }
            }
        }
    }
}

pub struct LogicalOpUnit {
    pending: Option<DispatchedOp>,
}
impl ExecutionUnit for LogicalOpUnit {
    fn new() -> Self { Self { pending: None } }
    fn is_busy(&self) -> bool { self.pending.is_some() }
    fn prepare(&mut self, op: &DispatchedOp) {
        *self = Self { pending: Some(op.clone()) }
    }

    fn execute(&mut self) {
        if let Some(ref mut ifo) = self.pending {
            let res = match ifo.uop {
                FunctionalUnitOp::Logical(op) => match op {
                    LogicalOp::Xor => ifo.x.bitxor(ifo.y),
                    LogicalOp::Or  => ifo.x.bitor(ifo.y),
                    LogicalOp::And => ifo.x.bitand(ifo.y),
                    LogicalOp::Sll => ifo.x.checked_shl(ifo.y).unwrap_or(0),
                    LogicalOp::Srl => ifo.x.checked_shr(ifo.y).unwrap_or(0),
                    LogicalOp::Sra => {
                        match ifo.x.checked_shr(ifo.y) {
                            Some(res) => res,
                            None => {
                                println!("sra {:08x} << {}", ifo.x, ifo.y);
                                0
                            }
                        }
                    },
                },
                _ => unimplemented!(),
            };
            ifo.res = Some(res);
            println!("[execute] LOU completed with {:08x}", res);
        } else {
            println!("[execute] LOU was empty");
        }
    }
    fn complete(&mut self) -> Option<DispatchedOp> {
        match &self.pending {
            None => None,
            Some(op) => {
                if op.res.is_some() {
                    self.pending.take()
                } else {
                    None
                }
            }
        }
    }
}

pub struct ComparatorUnit {
    pending: Option<DispatchedOp>,
}
impl ExecutionUnit for ComparatorUnit {
    fn new() -> Self { Self { pending: None } }
    fn is_busy(&self) -> bool { self.pending.is_some() }
    fn prepare(&mut self, op: &DispatchedOp) {
        *self = Self { pending: Some(op.clone()) }
    }


    fn execute(&mut self) {
        if let Some(ref mut ifo) = self.pending {
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
            ifo.res = Some(res);
            println!("[execute] CRU completed with {:08x}", res);
        } else {
            println!("[execute] CRU was empty");
        }
    }
    fn complete(&mut self) -> Option<DispatchedOp> {
        match &self.pending {
            None => None,
            Some(op) => {
                if op.res.is_some() {
                    self.pending.take()
                } else {
                    None
                }
            }
        }
    }

}
