from enum import Enum
from .base import BaseIo

class MonitorCmd:
    SRC = 0x0

class MonitorSource:
    ANALOG_IN_1 = 0
    ANALOG_IN_2 = 1
    ANALOG_OUT_1 = 2
    ANALOG_OUT_2 = 3
    DIGITAL_IO = 4
    PWM = 5
    XADC = 6
    SYNC = 7

class Monitor(BaseIo):
    def __init__(self, addr):
        super().__init__(addr)

    def source(self, t: int, src: MonitorSource):
        if src not in MonitorSource.__dict__.values():
            raise Exception(f"Monitor source value {src} is not valid.")
        self.add_instruction(t=t, cmd=MonitorCmd.SRC, data=src)

    def acquire(self, t: int, samples: int, dec: int = 1, label: str | None = None):
        self.add_acquisition(t=t, samples=samples, dec=dec, label=label)