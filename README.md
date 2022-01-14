# rvre 

`rvre` (like "reverie!") is my toy RISC-V (RV32I) core.

This project is an exercise in building a RISC-V machine that is slightly more 
complicated than the *in-order* implementations of machines that are used in
most of the existing instructional material in this space (as of ~2021).

My motivations for this are three-fold:

- Explore the design space for pipelined, out-of-order machines
- Suffer the process and try to de-mystify things
- Produce some kind of working [and ideally, synthesizable] soft RISC-V core

`rvre` is implemented with 
[Amaranth HDL](https://github.com/amaranth-lang/amaranth), mostly because:

- It seemed less-painful to pick up for beginners with little HDL experience
- I don't care to learn Scala/Chisel or deal with things in the Java ecosystem


