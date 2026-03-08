from .rp_base import Rp_base
from ..io.analog import AnalogIn, AnalogOut
from ..io.digital import DigitalIo
from ..io.pwm import Pwm
from ..io.scope import Scope
from ..io.sync import Sync    
from ..io.led import Led
import os

class Rp_125_14_Z7010(Rp_base):
    CLK_FREQ = 125e6
    IO_DICT = {
        "analog_out_1": {"class": AnalogOut, "addr": 0x0},
        "analog_out_2": {"class": AnalogOut, "addr": 0x1},
        #"analog_in_1": {"class": AnalogIn, "addr": 0x2}, #TODO: Implement configurable analog input 1
        #"analog_in_2": {"class": AnalogIn, "addr": 0x3}, #TODO: Implement configurable analog input 2
        "digital_io_1": {"class": DigitalIo, "addr": 0x4},
        "digital_io_2": {"class": DigitalIo, "addr": 0x5},
        "digital_io_3": {"class": DigitalIo, "addr": 0x6},
        "digital_io_4": {"class": DigitalIo, "addr": 0x7},
        "pwm_1": {"class": Pwm, "addr": 0x8},
        "pwm_2": {"class": Pwm, "addr": 0x9},
        "pwm_3": {"class": Pwm, "addr": 0xA},
        "pwm_4": {"class": Pwm, "addr": 0xB},
        "scope_1": {"class": Scope, "addr": 0xC},    
        "scope_2": {"class": Scope, "addr": 0xD},
        "led": {"class": Led, "addr": 0xE},
        "_sync": {"class": Sync, "addr": 0xF}
    }
    MMAP_DICT = {
        "pl" : {"addr": 0x4000_0000, "size": 0x0010_0000},
        "mem_instr" : {"addr": 0x0100_0000, "size": 0x0100_0000},
        "mem_scope_1" : {"addr": 0x0200_0000, "size": 0x0080_0000},
        "mem_scope_2" : {"addr": 0x0280_0000, "size": 0x0080_0000}
    }
    ADDR_DICT = {
        "reg_bank_err" : 0x4000_0000, 
        "reg_bank_done" : 0x4000_0004,
        "reg_bank_sync_counter" : 0x4000_0008,
        "reg_bank_en" : 0x4000_0040,
        "reg_bank_flush" : 0x4000_0044,
        "reg_bank_scope_1_samples" : 0x4000_0048,
        "reg_bank_scope_2_samples" : 0x4000_004C,
        "dma_instr" : 0x4001_0000,
        "dma_scope_1" : 0x4002_0000,
        "dma_scope_2" : 0x4003_0000
    }
    BITSTREAM = os.path.join(os.path.dirname(__file__), "../bitstream/io_sync_rp_125_14_z7010.bit")


    def __init__(self, ip: str, label: str = "rp_125_14_z7010"):
        
        super().__init__(ip, label)
