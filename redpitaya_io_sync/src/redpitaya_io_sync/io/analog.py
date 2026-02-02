from .base import BaseIo

class AnalogCmd:
    PHASE = 0x0
    PHASE_RST = 0x1
    FREQ = 0x2
    AMPL = 0x3

class AnalogBase(BaseIo):
    def __init__(self, addr, clk_freq):
        super().__init__(addr)
        self.clk_freq = clk_freq

    def frequency(self, t: int, val: int, update: bool = True):
        FREQ_MIN = -self.clk_freq / 2
        FREQ_MAX = self.clk_freq / 2
        if (val < FREQ_MIN) or (val > FREQ_MAX):
            raise Exception(f"Frequency value {val} is out of range [{FREQ_MIN}, {FREQ_MAX}].")
        data = int(val / self.clk_freq * (1 << 31)) | (int(update) << 31)
        self.add_instruction(t=t, cmd=AnalogCmd.FREQ, data=data)

    def phase(self, t: int, val: int, update: bool = True):
        data = int((val % 360) / 360 * (1 << 31)) | (int(update) << 31)
        self.add_instruction(t=t, cmd=AnalogCmd.PHASE, data=data)
    
    def amplitude(self, t: int, val: int, update: bool = True):
        AMPL_MIN = -1
        AMPL_MAX = 1
        if (val < AMPL_MIN) or (val > AMPL_MAX):
            raise Exception(f"Amplitude value {val} is out of range [{AMPL_MIN}, {AMPL_MAX}].")
        data = int(val * ((1 << 15) - 1)) | (int(update) << 31)
        self.add_instruction(t=t, cmd=AnalogCmd.AMPL, data=data)

    def phase_reset(self, t: int, update: bool = True):
        data = int(update) << 31
        self.add_instruction(t=t, cmd=AnalogCmd.PHASE_RST, data=data)


class AnalogOut(AnalogBase):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)
       

class AnalogIn(AnalogBase):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)

    def acquire(self, t: int, samples: int, dec: int = 1, label: str | None = None):
        self.add_acquisition(t=t, samples=samples, dec=dec, label=label)

