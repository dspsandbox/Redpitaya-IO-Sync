class TriggerSource:
    TrigNone = 0x0
    TrigImmediate = 0x1
    TrigTimeout = 0x2
    TrigExtHigh = 0x3
    TrigExtLow = 0x4
    TrigExtRise = 0x5
    TrigExtFall = 0x6
    TrigExtRiseFall = 0x7



from .base import BaseIo

class Sync (BaseIo):
    _requires_done_instruction = False

    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)

    def trigger(self, src: int, timeout: int = 0):
        TIMEOUT_MIN = 0
        TIMEOUT_MAX = (1 << 32) - 1
        if src not in TriggerSource.__dict__.values(): 
            raise Exception(f"Trigger source {src} is not valid.")
        if timeout is None:
            timeout = TIMEOUT_MAX
        if not (TIMEOUT_MIN <= timeout <= TIMEOUT_MAX):
            raise Exception(f"Timeout {timeout} is out of range ({TIMEOUT_MIN}-{TIMEOUT_MAX}).")

        self._add_instruction(cmd=src, data=timeout)

