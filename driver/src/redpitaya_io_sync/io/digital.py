from enum import Enum
from .base import BaseIo

class DigitalIoCmd(Enum):
    OUTPUT = 0x0
    TRISTATE = 0x1

class DigitalIo(BaseIo):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)

    def output(self, val: int, mask: int = 0xffff):
        self._add_instruction(cmd=DigitalIoCmd.OUTPUT.value,  data=((mask << 16) | val))
        
    def tristate(self, val: int, mask: int = 0xffff):
        self._add_instruction(cmd=DigitalIoCmd.TRISTATE.value, data=((mask << 16) | val))

    