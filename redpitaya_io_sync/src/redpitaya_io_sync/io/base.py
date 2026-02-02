import numpy as np

class BaseIoCmd:
    NOP = 0xF
    ACQ = 0xE
    ACQ_TLAST = 0xD
    SYNC_IDLE = 0xC



PREALLOCATION_BLOCK_LEN = 1024

class BaseIo():
    def __init__(self, addr):
        self._addr = addr
        self._t_last = -1
        self._t_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._mask_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint32)
        self._acq_dict = {}
        self._idx = 0
        self.changed = False
    
    def reset(self):
        self._t_last = -1
        self._t_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._mask_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint32)
        self._acq_dict = {}
        self._idx = 0
        self.changed = False


    

    def add_instruction(self, t: int, cmd: int, data: int, mask: int = 0xffffffff):
        #63 - 60 | 59 - 56 | 55 - 32 | 31 - 0
        #Addr  |   Cmd  |   Time   |   Data

        if t <= self._t_last:
            idx_previous_list = np.where(self._t_list == t)[0]
            if len(idx_previous_list):
                idx_previous = idx_previous_list[0]
                cmd_previous = (self._instr_list[idx_previous] >> 56) & 0xf
                #Found pre-existing NOP instruction
                if cmd_previous == BaseIoCmd.NOP:  
                    self._instr_list[idx_previous] = (
                        (self._instr_list[idx_previous] & 0xf0ffffff00000000) |
                        (cmd << 56) |
                        (data)
                    )
                    self._mask_list[idx_previous] = mask
                #Found pre-existing instruction with equal cmd but without mask overlap
                elif (cmd == cmd_previous) and not (mask & self._mask_list[idx_previous]): 
                    self._instr_list[idx_previous] |= (data & mask)
                    self._mask_list[idx_previous] |= mask

                #Found pre-existing different instructions with different cmd and/or mask overlap
                else:
                    raise Exception(f"Cannot overwrite pre-existing instruction at t={t}.")
                
        else:

            #Insert NOP instructions wherever every 2^24 clk cycles
            while (t - self._t_last) > (1<<24):
                self.add_instruction(self._t_last + (1 << 24), BaseIoCmd.NOP, 0, 0)

            #Create new instruction
            instr = ((self._addr << 60) | (cmd << 56) | ((t & 0xffffff) << 32) | (data & mask))
            
            #Preallocate more space if needed
            if self._idx >= len(self._instr_list):
                self._instr_list = np.concatenate((self._instr_list, np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)))
                self._t_list = np.concatenate((self._t_list,  np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)))
                self._mask_list = np.concatenate((self._mask_list,  np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint32)))

            #Add instruction to list
            self._instr_list[self._idx] = instr
            self._t_list[self._idx] = t
            self._mask_list[self._idx] = mask
            self._idx += 1
            self._t_last = max(self._t_last, t)
            self.changed = True

    
    def _sort(self):
        idx_sorted = np.argsort(self._t_list[:self._idx])
        self._t_list[:self._idx] = self._t_list[idx_sorted]
        self._instr_list[:self._idx] = self._instr_list[idx_sorted]
        self._mask_list[:self._idx] = self._mask_list[idx_sorted]
        self._sorted = True

    def add_acquisition(self, t: int, samples: int, dec : int,  label: str | None = None, tlast=False):
        
        #Check acquisition parameters
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
        
        #Determine command type and acquisition time window
        cmd = BaseIoCmd.ACQ_TLAST if tlast else BaseIoCmd.ACQ
        dec_pow_2 = int(np.log2(dec))
        acq_label = label
        acq_t_start = t
        acq_t_end = t + samples * dec
        
        #Check for overlapping acquisitions
        for _acq_label in self._acq_dict.keys():
            _acq_t_start = self._acq_dict[acq_label]['t']
            _acq_t_end = self._acq_dict[acq_label]['t'] + self._acq_dict[acq_label]['samples'] * self._acq_dict[acq_label]['dec']  
            
            if (acq_t_start < _acq_t_end) and (_acq_t_start < acq_t_end):
                raise Exception(f"Acquisition overlaps with previous acquisition '{_acq_label}' from t={_acq_t_start} to t={_acq_t_end}.")

        #Generate default label if none provided
        if label is None:
            label = f"acq_t{t}"
        
        #Check for duplicate labels
        if label in self._acq_dict:
            raise Exception(f"Acquisition label '{label}' already exists.")
        
        #Add acquisition instruction
        self.add_instruction(t=t, cmd=cmd, data=((dec_pow_2 << 24) | samples), mask=0xffffffff)
        self._acq_dict[label] = {'t': t, 'samples': samples, 'dec': dec}


    def add_sync_idle(self, t: int):
        self.add_instruction(t=t, cmd=BaseIoCmd.SYNC_IDLE, data=0, mask=0)
        
            
    def get_instruction_list(self):
        if not self._sorted:
            self._sort()
        return self._instr_list[:self._idx]
    
    def get_acquisition_dict(self):
        return self._acq_dict





