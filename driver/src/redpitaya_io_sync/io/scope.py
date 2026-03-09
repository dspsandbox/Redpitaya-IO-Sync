from .base import BaseIo
import numpy as np
from enum import Enum

class ScopeCmd(Enum):
    SRC = 0x0
    ACQ = 0x1
    DEC = 0x2

class ScopeSource(Enum):
    ANALOG_IN_1 = 0x0
    ANALOG_IN_2 = 0x1
    ANALOG_OUT_1 = 0x2
    ANALOG_OUT_2 = 0x3
    DIGITAL_IO_1 = 0x4
    DIGITAL_IO_2 = 0x5
    DIGITAL_IO_3 = 0x6
    DIGITAL_IO_4 = 0x7
    PWM_1 = 0x8
    PWM_2 = 0x9
    PWM_3 = 0xA
    PWM_4 = 0xB
    XADC_1 = 0xC
    XADC_2 = 0xD
    XADC_3 = 0xE
    XADC_4 = 0xF
    

class Scope(BaseIo):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)
        self._acq_dict = {}
        self._acq_samples = 0
        self._src = ScopeSource.ANALOG_IN_1
        self._dec = 1


    def reset(self):
        super().reset()
        self._acq_dict = {}
        self._acq_samples = 0

    def source(self, src: ScopeSource):
        if src not in ScopeSource:
            raise Exception(f"Scope source {src} is not valid. Should be of type ScopeSource")
        self._add_instruction(cmd=ScopeCmd.SRC.value, data=src.value)
        self._src = src

    def decimation(self, dec: int = 1):
        DEC_MIN = 1
        DEC_MAX = (1 << 32) - 1
        if (dec < DEC_MIN) or (dec > DEC_MAX):
            raise Exception(f"Decimation factor {dec} is out of range [{DEC_MIN}, {DEC_MAX}].")
            
        self._add_instruction(cmd=ScopeCmd.DEC.value, data=dec)
        self._dec = dec


    def acquire(self, samples: int, label: str | None = None):
        #Check Scope parameters
        SAMPLE_MIN = 1
        SAMPLE_MAX = (1 << 32) - 1 

        if (samples < SAMPLE_MIN) or (samples > SAMPLE_MAX):
            raise Exception(f"Number of samples {samples} is out of range [{SAMPLE_MIN}, {SAMPLE_MAX}].")
        
        #Determine command type 
        cmd = ScopeCmd.ACQ.value

        #Generate default label if none provided
        if label is None:
            label = f"acq_{len(self._acq_dict)}"
        
        #Check for duplicate labels
        if label in self._acq_dict:
            raise Exception(f"Acquisition label '{label}' already exists.")
        
        #Add Scope instruction
        self._acq_dict[label] = {'t': self._tnext, 'samples': samples,'src': self._src.name, 'dec': self._dec, 'addr': None}
        self._acq_samples += samples
        self._add_instruction(cmd=cmd, data=samples)
        
        
    def _get_acquisition_dict(self):
        return self._acq_dict


