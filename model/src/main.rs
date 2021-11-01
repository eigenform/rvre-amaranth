
pub mod prim;
pub mod unit;
pub mod rob;
pub mod rat;
pub mod sched;
pub mod rv32;

use rv32::isa::*;
use sched::*;
use prim::*;
use rat::*;
use rob::*;
use unit::*;

/// Initial state for the architectural registers.
const INIT_REG: [ArchRegValue; 8] = [
    ArchRegValue::Valid(0x00000000),
    ArchRegValue::Valid(0x11111111),
    ArchRegValue::Valid(0x22222222),
    ArchRegValue::Valid(0x33333333),
    ArchRegValue::Valid(0x44444444),
    ArchRegValue::Valid(0x55555555),
    ArchRegValue::Valid(0x66666666),
    ArchRegValue::Valid(0x77777777),
];

fn main() {
    let mut fpc = 0x0000_0000u32;
    let mut rat = RegisterAliasTable::new(8, Some(&INIT_REG));
    let mut rob = ReorderBuffer::new(16);
    let mut sch = Scheduler::new();
    let mut asu = AddSubUnit::new();
    let mut lou = LogicalOpUnit::new();
    let mut cru = ComparatorUnit::new();

    let mut next_inst: Opcode = rand::random();

    let mut fetch_stall = false;
    let mut sched_stall = false;

    for cycle in 0..64 {
        println!("======== Cycle {:04} ========", cycle);

        rob.print_status();

        // Fetch the next instruction
        next_inst = rand::random();
        fpc += 4;

        // Create a ROB entry for the next/current/newest instruction.
        println!("[decode] pc={:08x} {:?}", fpc, next_inst);
        let rob_entry = match next_inst {
            Opcode::Op(rd, ..) | 
            Opcode::OpImm(rd, ..) => {
                InFlightOp::new(fpc, StorageLoc::Reg(rd))
            },
            _ => unimplemented!(),
        };

        // Try to add this entry to the reorder buffer.
        match rob.push(rob_entry.clone()) {
            // No space in the ROB, so we need to stall.
            Err(e) => {
                println!("No space in ROB {:?}", e);
            },
            Ok(rob_idx) => {
                // Rename the destination register to the new ROB entry.
                match rob_entry.dst {
                    StorageLoc::Reg(rd) => {
                        rat[rd] = ArchRegValue::Name(rob_idx);
                        println!("[rename] mapped {:?} => p{}", rd, rob_idx); 
                    },
                    _ => unimplemented!(),
                }

                // Create a reservation entry for the next instruction.
                let reservation = match next_inst {
                    Opcode::Op(_, rs1, rs2, op) => {
                        let uop = op.to_uop();
                        ReservationEntry {
                            uop, rob_idx, dst: rob_entry.dst, stalled: 0,
                            op1: Operand::Reg(rs1), op2: Operand::Reg(rs2),
                        }
                    },
                    Opcode::OpImm(_, rs1, imm, op) => {
                        let uop = op.to_uop();
                        ReservationEntry {
                            uop, rob_idx, dst: rob_entry.dst, stalled: 0,
                            op1: Operand::Reg(rs1), op2: Operand::Imm(imm),
                        }
                    },
                    _ => unimplemented!(),
                };

                // Add the entry to the reservation stations.
                let res = sch.reserve(reservation);
                match res {
                    Ok(idx) => {
                        println!("[sched] reserved in slot {}", idx);
                    }
                    Err(_) => {
                        println!("[sched] no free reservation slot");
                    },
                }
            }
        }

        // Wake up any instructions that are ready to be dispatched
        // (consuming them from the reservation station slots).
        //
        // Then, dispatch operations to the functional units.

        sch.print_status();
        let mut dispatched = sched::dispatch(&mut sch, &rat, &rob);
        println!("[dispatch] dispatching {} uops", dispatched.len());
        for disp_op in dispatched.iter_mut() {
            match disp_op.uop {
                FunctionalUnitOp::AddSub(_)  => {
                    if !asu.is_busy() {
                        asu.prepare(disp_op);
                    }
                },
                FunctionalUnitOp::Logical(_) => {
                    if !lou.is_busy() {
                        lou.prepare(disp_op);
                    }
                },
                FunctionalUnitOp::Compare(_) => {
                    if !cru.is_busy() {
                        cru.prepare(disp_op);
                    }
                },
            };
        }



        // Execute any pending work in the execution units, then
        // write back any results to the ROB

        asu.execute();
        lou.execute();
        cru.execute();

        match asu.complete() {
            Some(op) => {
                rob.complete(op);
            },
            None => {
                println!("[complete] ASU couldn't complete");
            },
        }
        match lou.complete() {
            Some(op) => {
                rob.complete(op);
            },
            None => {
                println!("[complete] LOU couldn't complete");
            },
        }
        match cru.complete() {
            Some(op) => {
                rob.complete(op);
            },
            None => {
                println!("[complete] CRU couldn't complete");
            },
        }

        // Retire a single instruction from the ROB
        match rob.retire() {
            Some(op) => { println!("[retire] {:?}", op); },
            None => { println!("[retire] nothing to retire"); },
        }
        println!("");
    }


}


