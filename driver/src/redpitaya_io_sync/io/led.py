from enum import Enum
from .base import BaseIo

class LedCmd(Enum):
    WRITE = 0x0

class Led(BaseIo):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)

    def write(self, val: int, mask: int = 0xffff):
        self._add_instruction(cmd=LedCmd.WRITE.value,  data=((mask << 16) | val))
        

    