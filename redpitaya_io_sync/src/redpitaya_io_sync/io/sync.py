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
    def __init__(self, addr): 
        super().__init__(addr)

    def trigger(self, src: int, timeout: int = 0):
        TIMEOUT_MIN = 0
        TIMEOUT_MAX = (1 << (32 + 24)) - 1
        if src not in TriggerSource.__dict__.values(): 
            raise Exception(f"Trigger source {src} is not valid.")
        if not (TIMEOUT_MIN <= timeout <= TIMEOUT_MAX):
            raise Exception(f"Timeout {timeout} is out of range ({TIMEOUT_MIN}-{TIMEOUT_MAX}).")

        timeout_high = (timeout >> 32) & 0xffffff
        timeout_low = timeout & 0xffffffff
        self._add_instruction(cmd=src, t=timeout_high, data=timeout_low)

