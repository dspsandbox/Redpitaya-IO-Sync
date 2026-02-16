import numpy as np

class BaseIoCmd:
    NOP = 0xF
    DONE = 0xE



PREALLOCATION_BLOCK_LEN = 1024

class BaseIo():
    def __init__(self, addr):
        self._addr = addr
        self._t = -1
        self._t_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._mask_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint32)
        self._acq_dict = {}
        self._idx = 0
        self._preallocation_len = PREALLOCATION_BLOCK_LEN
        self._changed = False
    
    def reset(self):
        self._t = -1
        self._t_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._mask_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint32)
        self._acq_dict = {}
        self._idx = 0
        self._preallocation_len = PREALLOCATION_BLOCK_LEN
        self._changed = False

    def _get_idx(self):
        return self._idx 
    
    def _set_idx(self, val):
        self._idx = val


    def _add_instruction(self, cmd: int, t: int, data: int, mask: int = 0xffffffff):
        #63 - 60 | 59 - 56 | 55 - 32 | 31 - 0
        #Addr  |   Cmd  |   Time   |   Data

        if t <= self._t:
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
            while (t - self._t) > (1<<24):
                self._add_instruction(BaseIoCmd.NOP, self._t + (1 << 24), 0, 0)

            #Create new instruction
            instr = ((self._addr << 60) | (cmd << 56) | ((t & 0xffffff) << 32) | (data & mask))
            
            #Preallocate more space if needed
            if self._idx >= self._preallocation_len:
                self._instr_list = np.concatenate((self._instr_list, np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)))
                self._t_list = np.concatenate((self._t_list,  np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)))
                self._mask_list = np.concatenate((self._mask_list,  np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint32)))
                self._preallocation_len += PREALLOCATION_BLOCK_LEN

            #Add instruction to list
            self._instr_list[self._idx] = instr
            self._t_list[self._idx] = t
            self._mask_list[self._idx] = mask
            self._idx += 1
            self._t = max(self._t, t)
            self._changed = True

    

    def _sort_instructions(self):
        idx_sorted = np.argsort(self._t_list[:self._idx])
        self._t_list[:self._idx] = self._t_list[idx_sorted]
        self._instr_list[:self._idx] = self._instr_list[idx_sorted]
        self._mask_list[:self._idx] = self._mask_list[idx_sorted]

    def _set_done(self):
        t = self._t + 1
        self._add_instruction(BaseIoCmd.DONE, t=t, data=0, mask=0)
        
            
    def _get_instruction_list(self):
        self._changed = False
        return self._t_list[:self._idx], self._instr_list[:self._idx]
    
    def _get_time_list(self):
        return self._t_list[:self._idx]
    
    def _has_changed(self):
        return self._changed
    




