from io.analog import AnalogIn, AnalogOut
from io.digital import DigitalIo
from io.pwm import Pwm
from io.scope import Scope
from io.sync import Sync    


class Rp_125_14_base:
    def __init__(self, ip: str):
        self.ip = ip

        self.clk_freq = 125e6

        self.io_dict = {
            "analog_out_1": {"class": AnalogOut, "addr": 0x0},
            "analog_out_2": {"class": AnalogOut, "addr": 0x1},
            "analog_in_1": {"class": AnalogIn, "addr": 0x2},
            "analog_in_2": {"class": AnalogIn, "addr": 0x3},
            "digital_io": {"class": DigitalIo, "addr": 0x4},
            "pwm_1": {"class": Pwm, "addr": 0x5},
            "pwm_2": {"class": Pwm, "addr": 0x6},
            "pwm_3": {"class": Pwm, "addr": 0x7},
            "pwm_4": {"class": Pwm, "addr": 0x8},
            "scope_1": {"class": Scope, "addr": 0x9},    
            "scope_2": {"class": Scope, "addr": 0xA},
            "_sync": {"class": Sync, "addr": 0xB}
        }
       

    
