
use crate::prim::*;
use crate::rat::*;
use crate::rob::*;
use crate::unit::*;


/// Token for an operand.
#[derive(Debug, Copy, Clone)]
pub enum Operand {
    /// An architectural register.
    Reg(ArchReg),
    /// A signed immediate value.
    Imm(i32),
}
impl Operand {
    pub fn resolve(&self, rat: &RegisterAliasTable, rob: &ReorderBuffer) 
                                                            -> Option<u32> {
        match self {
            Self::Imm(data) => Some(*data as u32),
            Self::Reg(reg) => rat.resolve(*reg, rob),
        }
    }
}

#[derive(Debug, Clone)]
pub struct ReservationEntry {
    pub uop: FunctionalUnitOp,
    pub dst: StorageLoc,
    pub rob_idx: usize,
    pub op1:  Operand,
    pub op2:  Operand,
    pub stalled: usize,
}
impl ReservationEntry {
    pub fn resolve(&self, rat: &RegisterAliasTable, rob: &ReorderBuffer)
        -> Option<DispatchedOp> 
    {
        let data_x = self.op1.resolve(rat, rob);
        let data_y = self.op2.resolve(rat, rob);

        if data_x.is_some() && data_y.is_some() {
            Some(DispatchedOp {
                uop: self.uop,
                dst: self.dst,
                res: None,
                rob_idx: self.rob_idx,
                x: data_x.unwrap(),
                y: data_y.unwrap(),
            })
        } else {
            None
        }
    }
}

#[derive(Debug, Clone)]
pub struct DispatchedOp {
    pub uop: FunctionalUnitOp,
    pub dst: StorageLoc,
    pub res: Option<u32>,
    pub rob_idx: usize,
    pub x: u32,
    pub y: u32,
}

pub struct Scheduler {
    pub slots: [Option<ReservationEntry>; 4],
}
impl Scheduler {
    pub fn new() -> Self {
        Self {
            slots: [None, None, None, None],
        }
    }
    pub fn is_full(&self) -> bool {
        self.slots.iter().all(|x| x.is_some())
    }

    pub fn free_slots(&self) -> usize {
        self.slots.iter().filter(|x| x.is_none()).count()
    }
    pub fn print_status(&self) {
        for (idx, slot) in self.slots.iter().enumerate() {
            match slot {
                None => println!("[sched] slot {} free", idx),
                Some(entry) => {
                    println!("[sched] slot {} waiting for {} cycles", 
                             idx, entry.stalled);
                }
            }
        }
    }

    pub fn reserve(&mut self, e: ReservationEntry) -> Result<usize, ()> {
        for (idx, slot) in self.slots.iter_mut().enumerate() {
            if slot.is_none() {
                *slot = Some(e);
                return Ok(idx);
            }
        }
        return Err(());
    }

    pub fn dispatch(&mut self, rat: &RegisterAliasTable, rob: &ReorderBuffer) {
        let mut res: Vec<DispatchedOp> = Vec::new();
        for slot in self.slots.iter_mut().filter(|x| x.is_some()) {
            let mut entry  = slot.as_mut().unwrap();
            match entry.resolve(rat, rob) {
                Some(op) => {
                    res.push(op);
                    *slot = None;
                },
                None => {
                    entry.stalled += 1;
                },
            }
        }
        println!("{:08x?}", res);
    }
}

pub fn dispatch(sch: &mut Scheduler, rat: &RegisterAliasTable, 
    rob: &ReorderBuffer) -> Vec<DispatchedOp> 
{
    let mut res: Vec<DispatchedOp> = Vec::new();
    for slot in sch.slots.iter_mut().filter(|x| x.is_some()) {
        let entry  = slot.as_mut().unwrap();
        match entry.resolve(rat, rob) {
            Some(op) => {
                res.push(op);
                *slot = None;
            },
            None => {},
        }
    }
    res
}





