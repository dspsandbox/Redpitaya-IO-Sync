from .base import BaseIo

class DigitalIoCmd:
    OUTPUT = 0x0
    TRISTATE = 0x1

class DigitalIo(BaseIo):
    def __init__(self, addr):
        super().__init__(addr)

    def output(self, t: int, val: int, mask: int = 0xffffffff):
        self._add_instruction(cmd=DigitalIoCmd.OUTPUT, t=t, data=val, mask=mask)
        
    def tristate(self, t: int, val: int, mask: int = 0xffffffff):
        self._add_instruction(cmd=DigitalIoCmd.TRISTATE, t=t, data=val, mask=mask)

    