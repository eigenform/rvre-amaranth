
from amaranth import *
from amaranth.sim import *
from amaranth.back import verilog

from rvre.core import *
from rvre.fetch import *
from rvre.decode import *
from rvre.rf import *
from rvre.alu import *
from rvre.cam import *

# NOTE: Right now, the fetch unit is just a ROM
def read_test_rom():
    from struct import unpack
    with open("fw/test.bin", "rb") as f:
        data = bytearray(f.read())
    res = unpack("<{}L".format(len(data)//4), data)
    return res


def test_cam():
    INIT_CAM = [ 0x00, 0x00, 0x00, 0x00, 0x00, 0x55, 0x00, 0x00 ]
    def proc():

        # Read the address of 0x55
        yield dut.i_op.eq(CAMOp.READ)
        yield dut.i_data.eq(0x55)
        yield dut.i_en.eq(1)
        yield Tick()
        yield Settle()
        match = yield dut.o_match
        addr  = yield dut.o_addr
        valid = yield dut.o_valid
        assert (valid and (match == 1) and (addr == 5))
        yield dut.i_en.eq(0)
        yield Tick()
        yield Settle()

        # Write 0x66 to address 0x6
        yield dut.i_op.eq(CAMOp.WRITE)
        yield dut.i_data.eq(0x66)
        yield dut.i_addr.eq(6)
        yield dut.i_en.eq(1)
        yield Tick()
        yield Settle()
        valid = yield dut.o_valid
        assert valid
        yield dut.i_en.eq(0)
        yield Tick()
        yield Settle()

        # Read the address of 0x66
        yield dut.i_op.eq(CAMOp.READ)
        yield dut.i_data.eq(0x66)
        yield dut.i_en.eq(1)
        yield Tick()
        yield Settle()
        match = yield dut.o_match
        addr  = yield dut.o_addr
        valid = yield dut.o_valid
        assert (valid and (match == 1) and (addr == 6))
        yield dut.i_en.eq(0)
        yield Tick()
        yield Settle()

    dut = CAM(8, 8, init=INIT_CAM)
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)
    sim.run()

def test_fetch_unit():
    ROM = read_test_rom()
    def proc():
        pc = 0x00000000
        for word in ROM:
            yield dut.i_pc.eq(pc)
            yield Tick()
            yield Settle()
            pc  = yield dut.i_pc
            addr = yield dut.addr
            res = yield dut.o_inst
            if word != res:
                raise Exception("expect {:08x}, got {:08x}".format(word, res))
            pc += 4
    dut = FetchUnit(rom_data=ROM)
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)
    sim.run()


def test_decoder_from_rom():
    ROM = read_test_rom()
    def proc():
        for word in ROM:
            yield dut.i_inst.eq(word)
            yield Settle()
            #uop = yield dut.o_uop
            illegal = yield dut.o_illegal
            if illegal == 1:
                raise Exception("illegal instruction {:08x}".format(word))
            rd = yield dut.o_rd
            rs1 = yield dut.o_rs1
            rs2 = yield dut.o_rs2
            imm = yield dut.o_imm
            ifmt = yield dut.o_ifmt
            #print("ifmt={} rd={} rs1={} rs2={} imm={}".format(
            #    InstFormat(ifmt),
            #    rd, rs1, rs2, "{:08x}".format(imm)
            #))
    dut = DecodeUnit()
    sim = Simulator(dut)
    sim.add_process(proc)
    sim.run()


def test_alu():
    TESTS = [
        (ALUOp.ADD, 0x00000001, 0xffffffff, 0x00000000),
        (ALUOp.ADD, 0x80000000, 0x80000000, 0x00000000),
        (ALUOp.SUB, 0x00000000, 0x00000001, 0xffffffff),
    ]
    def proc():
        for test in TESTS:
            exp = test[3]
            yield dut.i_op.eq(test[0])
            yield dut.i_x.eq(test[1])
            yield dut.i_y.eq(test[2])
            yield Settle()
            res = yield dut.o_res
            if exp != res:
                raise Exception("got {:08x} exp {:08x}".format(res, exp))
    dut = ALU()
    sim = Simulator(dut)
    sim.add_process(proc)
    sim.run()


#def test_register_file():
#    def proc():
#        for reg_idx in range(0, 32):
#            yield dut.i_rd.eq(reg_idx)
#            yield dut.i_rd_data.eq(reg_idx << 24)
#            yield dut.i_rd_wen.eq(1)
#            yield dut.i_rs1.eq(reg_idx)
#            yield dut.i_rs2.eq(reg_idx)
#            yield Tick()
#            yield Settle()
#            rs1 = yield dut.o_rs1_data
#            rs2 = yield dut.o_rs2_data
#            assert rs1 == rs2 == (reg_idx << 24)
#    dut = RegisterFile()
#    sim = Simulator(dut)
#    sim.add_clock(1e-6)
#    sim.add_sync_process(proc)
#    sim.run()

def test_core():
    def proc():
        for cycle in range(0, 8):
            yield Tick()
    dut = RVRECore(rom_data=read_test_rom())
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)
    with sim.write_vcd(vcd_file="/tmp/core.vcd", gtkw_file="/tmp/core.gtkw"):
        sim.run()


def dump_verilog():
    #core = RVRECore(rom_data=read_test_rom())
    #core_v = verilog.convert(core, ports=core.ports())
    #with open("/tmp/core.v", "w") as f: f.write(core_v)

    dec = DecodeUnit()
    decoder_v = verilog.convert(dec, ports=dec.ports())
    with open("/tmp/decodeunit.v", "w") as f: f.write(decoder_v)

    cam = CAM(32, 32)
    cam_v = verilog.convert(cam, ports=cam.ports())
    with open("/tmp/cam.v", "w") as f: f.write(cam_v)



if __name__ == "__main__":
    test_cam()
    #test_register_file()
    test_fetch_unit()
    test_alu()
    test_decoder_from_rom()
    test_core()

    dump_verilog()


