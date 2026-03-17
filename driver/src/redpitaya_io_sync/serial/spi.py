
from ..io.digital import DigitalIo


class SPI:
    def __init__(self, io: DigitalIo, clk_div: int, cpol: int, cpha: int, sclk_mask: int = 0b0001, cs_mask: int = 0b0010, mosi_mask: int = 0b0100, miso_mask: int = 0b1000):
        
        if type(io) != DigitalIo:
            raise Exception(f"SPI requires a DigitalIo instance for IO control. Got {type(io)} instead.")
        
        if clk_div <= 0 or clk_div % 2 != 0:
            raise Exception("Clock divider must be a positive multiple of 2.")


        self._io = io
        self._clk_div = clk_div
        self._cpol = cpol
        self._cpha = cpha
        self._sclk_mask = sclk_mask
        self._cs_mask = cs_mask
        self._mosi_mask = mosi_mask
        self._miso_mask = miso_mask

    def io_config(self):
        self._io.tristate(val=self._miso_mask, mask=0xf)
        clk = self._cpol * self._sclk_mask
        cs = self._cs_mask
        mosi = 0 
        self._io.output(val=(clk |cs | mosi), mask=(self._sclk_mask | self._cs_mask | self._mosi_mask))

    def cs_low(self, wait: int=1):
        self._io.output(val=0, mask=self._cs_mask)
        self._io.wait(self._clk_div * wait)
    def cs_high(self, wait=1):
        self._io.wait(self._clk_div * wait)
        self._io.output(val=self._cs_mask, mask=self._cs_mask)
        
        

    def transfer(self, data: int, size: int):
        if size%2 != 0:
            raise Exception("Size must be a multiple of 2.")
   
        for i in range(size):
            mosi = ((data >> (size - 1 - i)) & 0x1) * self._mosi_mask
            clk = (self._cpol ^ self._cpha) * self._sclk_mask
            self._io.output(val=(mosi | clk), mask=(self._mosi_mask | self._sclk_mask))
            self._io.wait(self._clk_div // 2)
            clk ^= self._sclk_mask
            self._io.output(val=clk, mask=self._sclk_mask)
            self._io.wait(self._clk_div // 2)
        clk = self._cpol * self._sclk_mask
        self._io.output(val=clk, mask=self._sclk_mask)
