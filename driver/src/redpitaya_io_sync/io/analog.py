from .base import BaseIo
from enum import Enum

CLK_FREQ = 125e6

class AnalogCmd(Enum):
    PHASE = 0x0
    PHASE_RST = 0x1
    FREQ = 0x2
    AMPL = 0x3
    UPDATE = 0x8
    

class AnalogBase(BaseIo):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)

    def frequency(self, val: int, update: bool = True):
        FREQ_MIN = -self._clk_freq / 2
        FREQ_MAX = self._clk_freq / 2
        if (val < FREQ_MIN) or (val > FREQ_MAX):
            raise Exception(f"Frequency value {val} is out of range [{FREQ_MIN}, {FREQ_MAX}].")
        cmd = AnalogCmd.FREQ.value 
        if update: 
            cmd |= AnalogCmd.UPDATE.value
        data = int(val / self._clk_freq * ((1 << 32) - 1))         
        self._add_instruction(cmd=cmd, data=data)

    def phase(self, val: int, update: bool = True):
        cmd = AnalogCmd.PHASE.value 
        if update: 
            cmd |= AnalogCmd.UPDATE.value
        data = int((val % 360) / 360 * ((1 << 32) - 1)) 
        self._add_instruction(cmd=cmd,  data=data)
    
    def amplitude(self, val: int, update: bool = True):
        AMPL_MIN = -1
        AMPL_MAX = 1
        if (val < AMPL_MIN) or (val > AMPL_MAX):
            raise Exception(f"Amplitude value {val} is out of range [{AMPL_MIN}, {AMPL_MAX}].")
        
        cmd = AnalogCmd.AMPL.value
        if update: 
            cmd |= AnalogCmd.UPDATE.value
        data = int(val * ((1 << 15) - 1)) 
        self._add_instruction(cmd=cmd, data=data)

    def phase_reset(self, update: bool = True):
        data = 1
        cmd = AnalogCmd.PHASE_RST.value 
        if update: 
            cmd |= AnalogCmd.UPDATE.value
        self._add_instruction(cmd=cmd, data=data)


class AnalogOut(AnalogBase):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)
       
class AnalogIn(AnalogBase):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)

    

