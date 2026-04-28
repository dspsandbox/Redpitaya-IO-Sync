from __future__ import annotations
from .base import BaseIo
import numpy as np
from enum import Enum

class ScopeCmd(Enum):
    SRC = 0x0
    ACQ = 0x1
    DEC = 0x2

class ScopeSource(Enum):
    RF_IN_0 = 0x0
    RF_IN_1 = 0x1
    RF_OUT_0 = 0x2
    RF_OUT_1 = 0x3
    DIGITAL_IO_0 = 0x4
    DIGITAL_IO_1 = 0x5
    DIGITAL_IO_2 = 0x6
    DIGITAL_IO_3 = 0x7
    ANALOG_OUT_0 = 0x8
    ANALOG_OUT_1 = 0x9
    ANALOG_OUT_2 = 0xA
    ANALOG_OUT_3 = 0xB
    ANALOG_IN_0 = 0xE
    ANALOG_IN_1 = 0xC
    ANALOG_IN_2 = 0xD
    ANALOG_IN_3 = 0xF
    

class Scope(BaseIo):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)
        self._acq_dict = {}
        self._acq_samples = 0
        self._src = None
        self._dec = None


    def reset(self):
        super().reset()
        self._acq_dict = {}
        self._acq_samples = 0
        self._src = None
        self._dec = None

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


    def acquire(self, samples: int, label: str | None = None, run_async: bool = False):
        #Check Scope parameters
        SAMPLE_MIN = 1
        SAMPLE_MAX = (1 << 32) - 1 

        if (samples < SAMPLE_MIN) or (samples > SAMPLE_MAX):
            raise Exception(f"Number of samples {samples} is out of range [{SAMPLE_MIN}, {SAMPLE_MAX}].")
        
        if self._src is None:
            raise Exception("Scope source not set within current IoSyncFrame. Please set scope source before acquiring.")
        if self._dec is None:
            raise Exception("Scope decimation not set within current IoSyncFrame. Please set scope decimation before acquiring.")
        
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

        if run_async:
            duration = 1
        else:  
            duration = samples * self._dec + 1
        self._add_instruction(cmd=cmd, data=samples, duration=duration)
        
        
    def _get_acquisition_dict(self):
        return self._acq_dict


