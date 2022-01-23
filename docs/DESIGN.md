
# Design Notes

This is my [informal, working] specification and rationale for the RVRE 
microarchitecture. Many aspects of this should be parameterizable, so I'm 
going to try to avoid talking about those details until it's necessary.

## About Out-of-Order Machines

Out-of-order machines typically have a "front-end"/"back-end" distinction 
between parts of the pipeline. The front-end is concerned with bringing
instructions into the machine, mostly in the original program order.
The back-end deals with performing instructions and making changes to the 
programmer-visible state (also called the "architectural state") of the 
machine.

At the interface between these two, a program is partially converted into some 
kind of representation that is more amenable to being parallelized.

The principles behind out-of-order machines are similar to those applied in
the design of optimizing compilers: a program is incrementally transformed 
into some kind of representation where only true data dependences remain.
These dependences are sometimes called "Read-after-Write" (RAW) dependences.
(true data dependences are also called "Read-after-Write (RAW) hazards").

Compilers accomplish this by transforming programs into a "single static 
assignment" (SSA) form, where the resulting values from instructions are 
assigned to unique storage locations. This obviates the producer-consumer 
relationships (true dependences) between instructions, because there are no 
cases where the "architectural storage locations" (general-purpose registers 
defined by an ISA) are aliasing. 

## Front-End

These are different components in the front-end part of the machine.

### Next Program Counter 
The machine has a **program counter**: a memory address indicating the
location of the next instruction. The value of the next program counter
may be:

- The next sequential address
- The result of an instruction (a branching operation)
- The address of a predicted branch

Branch prediction is effectively *necessary* in out-of-order machines, but I 
haven't put any thought into a scheme for it yet.

### Instruction Fetch
A **fetch unit** uses the program counter to read the next instruction from a 
memory device. 

Until I get around to implementing a cache and doing some kind of AXI/Wishbone 
interface to external memories, the instruction memory is going to be a ROM 
baked directly into the fetch unit.

### Instruction Decode
A **decode unit** decomposes instructions into one or more sets of distinct 
control signals which are used by different parts in the machine. 

A set of these control signals can also be called a "micro-op" (or "uop"), and 
represents a discrete unit of work that needs to be done in the machine.
Most (but not all) components of a uop can be derived by the decode unit:

- The type of functional unit used to perform this operation
- The particular kind of operation
- The names of architectural storage locations used as operands
- Any immediate data encoded in an instruction

## Backend

These are the different components in the back-end part of the machine.

### Physical Register File
In this machine, there is a [unified] **physical register file** (PRF) that 
holds all of the data values produced by instructions. The PRF has read/write
ports for each execution unit in the machine.

### Register Alias Table
First, in order to make dependences between instructions more explicit, the 
machine needs to have more storage locations than are architecturally defined 
(i.e. the RISC-V ISA defines 32 general-purpose registers).

A **register alias table** has one entry for each architectural register.
Each entry associates an architectural register with the name of the 
most-recent PRF entry it is bound to.

Immediately after the decode unit, any *source register operands* of a uop are 
sent to the RAT and resolved into physical register names.

### Register Free/Busy List
A **free-list** has a bit for each PRF entry, and indicates whether or not
a physical register is currently available. 

Destination register operands are renamed by finding a free physical register
in the list. After a uop has retired (and it's result is unused), the physical
register is reclaimed.

### Reorder Buffer
A **reorder buffer** is a circular queue which tracks the original order
in which uops enter the machine. 

Uops enter the machine at the newest (head) entry of the ROB, and exit when 
they become the oldest (tail entry) in the machine.

### Issue
Uops with renamed operands are placed into an **issue queue** after all of
their operands have been renamed, where they wait until they are ready to be 
executed. A uop "wakes up" from the issue queue when all of its source operand 
data is determined to be available.

### Execution
Different functional units are responsible for different kinds of uops.

- An **arithmetic/logic unit** performs some integer or logical operation
- An **address generation unit** computes an effective address
- A **branch unit** evaluates some condition and computes the destination of 
  a branching operation

A uop has completed after results have been written back to the PRF.
Completed operations set a corresponding bit in their associated ROB entry.

### Completion

Upon completion, an execution unit sends a message back to the issue queue,
indicating that the physical register associated with the resulting data
may be used to wake up instructions that are waiting.

### Retire
Retire control logic checks the oldest (tail) entry in the reorder buffer. 
If the entry has been marked as completed, it is removed and the results are 
made architecturally visible by updating the RAT.


