from .base import BaseIo
import numpy as np

class ScopeCmd:
    SRC = 0x0
    ACQ = 0x1
    ACQ_TLAST = 0x2

class ScopeSource:
    ANALOG_IN_1 = 0x0
    ANALOG_IN_2 = 0x1
    ANALOG_OUT_1 = 0x2
    ANALOG_OUT_2 = 0x3
    DIGITAL_IO_1 = 0x4
    DIGITAL_IO_2 = 0x5
    PWM_1 = 0x6
    PWM_2 = 0x7
    PWM_3 = 0x8
    PWM_4 = 0x9
    XADC_1 = 0xA
    XADC_2 = 0xB
    XADC_3 = 0xC
    XADC_4 = 0xD
    

class Scope(BaseIo):
    def __init__(self, addr, clk_freq):
        super().__init__(addr, clk_freq)
        self._acq_dict = {}
        self._idx_tlast = None

    def reset(self):
        super().reset()
        self._acq_dict = {}

    def source(self, src: ScopeSource):
        if src not in ScopeSource.__dict__.values():
            raise Exception(f"Scope source {src} is not valid.")
        self._add_instruction(cmd=ScopeCmd.SRC, data=src)


    def acquire(self, samples: int, dec: int = 1, label: str | None = None):
        #Check Scope parameters
        SAMPLE_MIN = 1
        SAMPLE_MAX = 1 << 24 
        DEC_MIN = 1 
        DEC_MAX = 1 << 32

        if (samples < SAMPLE_MIN) or (samples > SAMPLE_MAX):
            raise Exception(f"Number of samples {samples} is out of range [{SAMPLE_MIN}, {SAMPLE_MAX}].")
        if (dec < DEC_MIN) or (dec > DEC_MAX):
            raise Exception(f"Decimation factor {dec} is out of range [{DEC_MIN}, {DEC_MAX}].")
        if (dec & (dec - 1)) != 0:
            raise Exception(f"Decimation factor {dec} is not a power of 2.")
        
        #Determine command type and Scope time window
        cmd = ScopeCmd.ACQ
        dec_pow_2 = int(np.log2(dec))
        acq_t_start = self._tnext
        acq_t_end = acq_t_start + samples * dec
        
        #Check for overlapping Scopes
        for _acq_label in self._acq_dict.keys():
            _acq_t_start = self._acq_dict[_acq_label]['t']
            _acq_t_end = self._acq_dict[_acq_label]['t'] + self._acq_dict[_acq_label]['samples'] * self._acq_dict[_acq_label]['dec']  
            
            if (acq_t_start < _acq_t_end) and (_acq_t_start < acq_t_end):
                raise Exception(f"Acquisition overlaps with previous acquisition '{_acq_label}' from t={_acq_t_start} to t={_acq_t_end}.")

        #Generate default label if none provided
        if label is None:
            label = f"acq_t{acq_t_start}"
        
        #Check for duplicate labels
        if label in self._acq_dict:
            raise Exception(f"Acquisition label '{label}' already exists.")
        
        #Add Scope instruction
        self._add_instruction(cmd=cmd, data=((dec_pow_2 << 24) | samples), duration=samples * dec)
        self._acq_dict[label] = {'t': acq_t_start, 'samples': samples, 'dec': dec}

    def _acquire_tlast(self):
        samples = 1
        t = 0
        for _acq_label in self._acq_dict.keys():
            _acq_t_end = self._acq_dict[_acq_label]['t'] + self._acq_dict[_acq_label]['samples'] * self._acq_dict[_acq_label]['dec'] 
        t = max(t, _acq_t_end)

        self._add_instruction(cmd=ScopeCmd.ACQ_TLAST, data=samples, duration=1)
        
    def _get_acquisition_dict(self):
        return self._acq_dict
