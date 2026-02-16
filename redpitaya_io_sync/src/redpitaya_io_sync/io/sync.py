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
        if src not in TriggerSource.__dict__.values(): 
            raise Exception(f"Trigger source {src} is not valid.")
        self.add_instruction(t=0, cmd=src, data=timeout)

