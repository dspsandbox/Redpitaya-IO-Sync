from .base import BaseIo

class Xadc(BaseIo):
    def __init__(self, addr):
        super().__init__(addr)

    def acquire(self, t: int, samples: int, dec: int = 1, label: str | None = None):
        self.add_acquisition(t=t, samples=samples, dec=dec, label=label)

