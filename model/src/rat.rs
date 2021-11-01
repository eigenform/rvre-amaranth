//! Implementation of a register alias table.

use crate::prim::*;
use crate::rob::*;
use std::ops::{Index, IndexMut};

/// Token representing the value of an architectural register.
#[derive(Debug, Clone, Copy)]
pub enum ArchRegValue { 
    /// This register has a concrete value.
    Valid(u32), 
    /// This register is mapped to some microarchitectural register.
    Name(usize),
}

/// A register alias table (RAT).
///
/// This table maps names of architectural registers to either (a) a concrete 
/// value, or (b) the name of some microarchitectural register - i.e. an entry
/// in a [ReorderBuffer].
///
#[derive(Debug)]
pub struct RegisterAliasTable {
    size: usize,
    table: Vec<ArchRegValue>,
}
impl RegisterAliasTable {
    pub fn new(size: usize, initial_state: Option<&[ArchRegValue]>) -> Self {
        let mut res = Self {
            size,
            table: vec![ArchRegValue::Valid(0x0000_0000); size],
        };
        if let Some(init) = initial_state {
            assert_eq!(size, init.len());
            res.table.copy_from_slice(init);
        }
        res
    }

    /// Try to resolve the data associated with an [ArchReg].
    pub fn resolve(&self, r: ArchReg, rob: &ReorderBuffer) -> Option<u32> {
        match self[r] {
            ArchRegValue::Valid(data) => Some(data),
            ArchRegValue::Name(rob_idx) => {
                match rob.get(rob_idx) {
                    None => unimplemented!("invalid rob entry {:?}", rob_idx),
                    Some(rob_entry) => {
                        match rob_entry.result {
                            Some(data) => Some(data),
                            None => None,
                        }
                    }
                }
            }
        }
    }
}

impl Index<ArchReg> for RegisterAliasTable {
    type Output = ArchRegValue;
    fn index(&self, index: ArchReg) -> &Self::Output {
        assert!(index.0 < self.size);
        &self.table[index.0]
    }
}
impl IndexMut<ArchReg> for RegisterAliasTable {
    fn index_mut(&mut self, index: ArchReg) -> &mut Self::Output {
        assert!(index.0 < self.size);
        &mut self.table[index.0]
    }
}


