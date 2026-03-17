from enum import Enum
from .base import BaseIo

class LedCmd(Enum):
    OUTPUT = 0x0

class Led(BaseIo):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)

    def output(self, val: int, mask: int = 0xffff):
        self._add_instruction(cmd=LedCmd.OUTPUT.value,  data=((mask << 16) | val))
        

    