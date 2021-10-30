//! Implementation of a reorder buffer.

use std::ops::{Index, IndexMut};
use crate::prim::*;

#[derive(Debug, Clone, Copy)]
pub enum StorageLoc {
    /// The name (index) of an architectural register.
    Reg(ArchReg),
    /// The name (address) of a memory location.
    Mem(u32),
    /// If an instruction has no effect, why are we handling it?
    None,
}

/// An entry in some reorder buffer (ROB).
#[derive(Debug, Clone, Copy)]
pub struct ROBEntry {
    /// The program counter for this instruction.
    pub pc: u32,
    /// The storage location for the result value of this instruction.
    pub dst: StorageLoc,
    /// Embedded register/valid bit containing a result value.
    pub result: Option<u32>,
    /// Whether or not this instruction should raise an exception.
    pub fault: bool,
    /// Whether or not this instruction is ready to be committed/retired.
    pub complete: bool,
}
impl ROBEntry {
    pub fn new(pc: u32, dst: StorageLoc) -> Self {
        Self {
            pc, 
            dst,
            result: None,
            fault: false,
            complete: false,
        }
    }
}



pub struct ReorderBuffer {
    pub data: RingBuffer<ROBEntry>,
}
impl ReorderBuffer {
    pub fn new(size: usize) -> Self {
        Self {
            data: RingBuffer::new(16),
        }
    }
}

