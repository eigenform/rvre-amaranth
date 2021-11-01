//! Implementation of a reorder buffer.

use std::ops::{Index, IndexMut};
use crate::prim::*;
use crate::sched::*;



//#[derive(Debug)]
//pub struct ReorderBuffer {
//    pub data: RingBuffer<ROBEntry>,
//}
//impl ReorderBuffer {
//    pub fn new(size: usize) -> Self {
//        Self {
//            data: RingBuffer::new(16),
//        }
//    }
//    /// Complete some instruction, writing the result to the corresponding
//    /// entry in the ROB.
//    pub fn complete(&mut self, op: CompletedOp) {
//        println!("[complete] {:?}", op);
//        let mut entry = match self.data.get_mut(op.rob_idx) {
//            Some(e) => e,
//            None => panic!("no rob entry?"),
//        };
//        entry.result = Some(op.res);
//        entry.complete = true;
//    }
//    /// Retire the oldest instruction in the ROB, writing the effects back
//    /// to the architectural registers (or memory?)
//    pub fn retire(&mut self) {
//        match self.data.pop() {
//            Some((entry, idx)) => {
//                println!("[retire] pc={:08x}", entry.pc);
//            },
//            None => {
//                println!("[retire] we didn't retire anything!");
//            }
//        }
//    }
//}


// ----------------------------------------------------------------------

/// Token for a storage location, indicating where some result data will be
/// committed after an instruction has retired.
#[derive(Debug, Clone, Copy)]
pub enum StorageLoc {
    /// The name (index) of an architectural register.
    Reg(ArchReg),
    /// The name (address) of a memory location.
    Mem(u32),
    /// If an instruction has no effect, why are we handling it??
    None,
}


/// An in-flight instruction, stored in a [ReorderBuffer].
#[derive(Debug, Clone)]
pub struct InFlightOp {
    pub pc: u32,
    pub dst: StorageLoc,
    pub result: Option<u32>,
}
impl InFlightOp {
    pub fn new(pc: u32, dst: StorageLoc) -> Self {
        Self {
            pc, 
            dst,
            result: None,
        }
    }
    pub fn is_complete(&self) -> bool {
        self.result.is_some()
    }
}

/// Error code for transactions with a [ReorderBuffer].
#[derive(Debug)]
pub enum ROBError {
    /// The reorder buffer is full.
    Full,
    /// The reorder buffer is empty.
    Empty,
    /// An entry could not be removed from the reorder buffer.
    Incomplete,
}


#[derive(Debug)]
pub struct ReorderBuffer {
    data: Vec<Option<InFlightOp>>,
    retire_ptr: usize,
    issue_ptr: usize,
    size: usize,
}
impl ReorderBuffer {
    pub fn new(size: usize) -> Self {
        Self {
            size,
            retire_ptr: 0, 
            issue_ptr: 0,
            data: vec![None; size],
        }
    }

    pub fn print_status(&self) {
        let retire_ptr = self.retire_ptr;
        let issue_ptr = self.issue_ptr;

        fn fmt_ptr(rptr: usize, iptr: usize, idx: usize) -> &'static str {
            if (idx == rptr) && (idx == iptr) { "o" }
            else if idx == rptr { "r" }
            else if idx == iptr { "i" }
            else { "." }
        }

        for (idx, op) in self.data.iter().enumerate() {
            let fmtstr = fmt_ptr(retire_ptr, issue_ptr, idx);
            if op.is_none() {
                println!("[ROB{:02}] {} empty", idx, fmtstr);
                continue;
            }
            let x = op.as_ref().unwrap();
            println!("[ROB{:02}] {} pc={:08x} {:?} <= {:08x?}", 
                     idx, fmtstr, x.pc, x.dst, x.result);
        }
    }

    pub fn is_full(&self) -> bool {
        (self.retire_ptr == self.issue_ptr) && self.data[self.retire_ptr].is_some()
    }
    pub fn is_empty(&self) -> bool {
        self.data[self.retire_ptr].is_none()
    }
    pub fn push(&mut self, e: InFlightOp) -> Result<usize, ROBError> {
        if (self.retire_ptr == self.issue_ptr) && (self.data[self.retire_ptr].is_some()) {
            Err(ROBError::Full)
        } else {
            let issue_ptr = self.issue_ptr;
            self.data[self.issue_ptr] = Some(e);
            self.issue_ptr = (self.issue_ptr + 1) % self.size;
            Ok(issue_ptr)
        }
    }

    pub fn pop(&mut self) -> Result<InFlightOp, ROBError> {
        if self.data[self.retire_ptr].is_none() {
            Err(ROBError::Empty)
        } else {
            let retire_ptr = self.retire_ptr;
            if self.data[self.retire_ptr].as_ref().unwrap().is_complete() {
                let res = self.data[self.retire_ptr].take().unwrap();
                self.retire_ptr = (self.retire_ptr + 1) % self.size;
                Ok(res)
            } else {
                Err(ROBError::Incomplete)
            }
        }
    }
    pub fn get(&self, idx: usize) -> &Option<InFlightOp> {
        assert!(idx < self.size - 1);
        &self.data[idx]
    }
    pub fn get_mut(&mut self, idx: usize) -> &mut Option<InFlightOp> {
        assert!(idx < self.size - 1);
        &mut self.data[idx]
    }

    /// Retire the oldest instruction in the ROB, writing the effects back
    /// to the architectural registers (or memory?)
    pub fn retire(&mut self) -> Option<InFlightOp> {
        match self.pop() {
            Ok(e) => Some(e),
            Err(_e) => None,
        }
    }
    /// Complete some instruction, writing the result to the corresponding
    /// entry in the ROB.
    pub fn complete(&mut self, op: DispatchedOp) {
        println!("[complete] {:?}", op);
        let mut entry = match self.get_mut(op.rob_idx) {
            Some(e) => e,
            None => panic!("rob entry {} was None?", op.rob_idx),
        };
        let res = op.res.unwrap();
        entry.result = Some(res);
    }

}



