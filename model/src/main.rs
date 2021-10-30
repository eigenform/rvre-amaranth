
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

    for cycle in 0..32 {
        println!("======== Cycle {:04} ========", cycle);
        let mut fetch_stall = false;

        // Complete any pending work in the functional units.

        asu.execute();
        lou.execute();
        cru.execute();

        // Wake up any instructions that are ready to be dispatched
        // (consuming them from the reservation station slots).
        //
        // Then, dispatch operations to the functional units.

        sch.print_status();
        let dispatched = sched::dispatch(&mut sch, &rat, &rob);
        println!("[dispatch] dispatching {} uops", dispatched.len());
        for disp_op in dispatched.iter() {
            match disp_op.uop {
                FunctionalUnitOp::AddSub(_)  => asu.prepare(*disp_op),
                FunctionalUnitOp::Logical(_) => lou.prepare(*disp_op),
                FunctionalUnitOp::Compare(_) => cru.prepare(*disp_op),
            };
        }

        // If the ROB or reservation stations are full, we cannot schedule
        // this instruction, so we have to stall
        if rob.data.is_full() || sch.is_full() {
        }

        // Create a ROB entry for the next/current/newest instruction.
        let rob_entry = match next_inst {
            Opcode::Op(rd, ..) | 
            Opcode::OpImm(rd, ..) => {
                ROBEntry::new(fpc, StorageLoc::Reg(rd))
            },
            _ => unimplemented!(),
        };

        // Try to add this entry to the reorder buffer.
        let stall = match rob.data.push(rob_entry) {
            // No space in the ROB, so we need to stall.
            None => true,

            Some(idx) => {
                // Rename the destination register to the new ROB entry.
                match rob_entry.dst {
                    StorageLoc::Reg(rd) => {
                        rat[rd] = ArchRegValue::Name(idx);
                        println!("[rename] mapped {:?} => p{}", rd, idx); 
                    },
                    _ => unimplemented!(),
                }

                // Create a reservation entry for the next instruction.
                let reservation = match next_inst {
                    Opcode::Op(_, rs1, rs2, op) => {
                        let uop = op.to_uop();
                        ReservationEntry {
                            uop, dst: rob_entry.dst, stalled: 0,
                            op1: Operand::Reg(rs1),
                            op2: Operand::Reg(rs2),
                        }
                    },
                    Opcode::OpImm(_, rs1, imm, op) => {
                        let uop = op.to_uop();
                        ReservationEntry {
                            uop, dst: rob_entry.dst, stalled: 0,
                            op1: Operand::Reg(rs1),
                            op2: Operand::Imm(imm),
                        }
                    },
                    _ => unimplemented!(),
                };

                // Add the entry to the reservation stations.
                let res = sch.reserve(reservation);
                match res {
                    Ok(idx) => {
                        println!("[sched] reserved in slot {}", idx);
                        false
                    }
                    Err(_) => {
                        unimplemented!("no free reservation slot, stall");
                        true
                    },
                }
            }
        };


        // 8. Increment program counter
        fpc = fpc.wrapping_add(4);
        println!("");
    }


}







