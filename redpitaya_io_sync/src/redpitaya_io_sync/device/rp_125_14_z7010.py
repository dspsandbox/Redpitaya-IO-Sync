from .rp_base import Rp_base
from ..io.analog import AnalogIn, AnalogOut
from ..io.digital import DigitalIo
from ..io.pwm import Pwm
from ..io.scope import Scope
from ..io.sync import Sync    
import os

class Rp_125_14_Z7010(Rp_base):
    def __init__(self, ip: str, label: str = "rp_125_14_z7010"):
        self._clk_freq = 125e6
        self._io_dict = {
            "analog_out_1": {"class": AnalogOut, "addr": 0x0},
            "analog_out_2": {"class": AnalogOut, "addr": 0x1},
            "analog_in_1": {"class": AnalogIn, "addr": 0x2},
            "analog_in_2": {"class": AnalogIn, "addr": 0x3},
            "digital_io_1": {"class": DigitalIo, "addr": 0x4},
            "digital_io_2": {"class": DigitalIo, "addr": 0x5},
            "pwm_1": {"class": Pwm, "addr": 0x6},
            "pwm_2": {"class": Pwm, "addr": 0x7},
            "pwm_3": {"class": Pwm, "addr": 0x8},
            "pwm_4": {"class": Pwm, "addr": 0x9},
            "scope_1": {"class": Scope, "addr": 0xA},    
            "scope_2": {"class": Scope, "addr": 0xB},
            "_sync": {"class": Sync, "addr": 0xC}
        }
        self._mmap_range_dict = {
            "pl" : {"addr": 0x4000_0000, "size": 0x0010_0000},
            "mem_instr" : {"addr": 0x0100_0000, "size": 0x0100_0000},
            "mem_scope_1" : {"addr": 0x0200_0000, "size": 0x0050_0000},
            "mem_scope_2" : {"addr": 0x0250_0000, "size": 0x0050_0000}
        }
        self._addr_dict = {
            "reg_bank_err" : 0x4000_0000, 
            "reg_bank_done" : 0x4000_0004,
            "reg_bank_sync_counter" : 0x4000_0008,
            "reg_bank_en" : 0x4000_0040,
            "reg_bank_reset" : 0x4000_0044,
            "reg_bank_flush" : 0x4000_0048,
            "dma_instr" : 0x4001_0000,
            "dma_scope_0" : 0x4002_0000,
            "dma_scope_1" : 0x4003_0000
        }
        self._bitstream = os.path.join(os.path.dirname(__file__), "bitstream/io_sync_rp_125_14_z7010.bit")
        super().__init__(ip, label)
