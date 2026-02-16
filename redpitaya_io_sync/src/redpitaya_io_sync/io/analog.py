from .base import BaseIo

CLK_FREQ = 125e6

class AnalogCmd:
    PHASE = 0x0
    PHASE_RST = 0x1
    FREQ = 0x2
    AMPL = 0x3

class AnalogBase(BaseIo):
    def __init__(self, addr):
        super().__init__(addr)

    def frequency(self, t: int, val: int, update: bool = True):
        FREQ_MIN = -CLK_FREQ / 2
        FREQ_MAX = CLK_FREQ / 2
        if (val < FREQ_MIN) or (val > FREQ_MAX):
            raise Exception(f"Frequency value {val} is out of range [{FREQ_MIN}, {FREQ_MAX}].")
        data = int(val / CLK_FREQ * (1 << 31)) | (int(update) << 31)
        self.add_instruction(cmd=AnalogCmd.FREQ, t=t, data=data)

    def phase(self, t: int, val: int, update: bool = True):
        data = int((val % 360) / 360 * (1 << 31)) | (int(update) << 31)
        self._add_instruction(cmd=AnalogCmd.PHASE, t=t, data=data)
    
    def amplitude(self, t: int, val: int, update: bool = True):
        AMPL_MIN = -1
        AMPL_MAX = 1
        if (val < AMPL_MIN) or (val > AMPL_MAX):
            raise Exception(f"Amplitude value {val} is out of range [{AMPL_MIN}, {AMPL_MAX}].")
        data = int(val * ((1 << 15) - 1)) | (int(update) << 31)
        self._add_instruction(cmd=AnalogCmd.AMPL, t=t, data=data)

    def phase_reset(self, t: int, update: bool = True):
        data = int(update) << 31
        self._add_instruction(cmd=AnalogCmd.PHASE_RST, t=t, data=data)


class AnalogOut(AnalogBase):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)
       

class AnalogIn(AnalogBase):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)

    

