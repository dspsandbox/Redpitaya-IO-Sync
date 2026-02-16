import numpy as np

class BaseIoCmd:
    NOP = 0xF
    SYNC_IDLE = 0xE



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
        self.changed = False
    
    def reset(self):
        self._t = -1
        self._t_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._mask_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint32)
        self._acq_dict = {}
        self._idx = 0
        self.changed = False

    def _get_idx(self):
        return self._idx 
    
    def _set_idx(self, val):
        self._idx = val


    def _add_instruction(self, t: int, cmd: int, data: int, mask: int = 0xffffffff):
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
                self._add_instruction(self._t + (1 << 24), BaseIoCmd.NOP, 0, 0)

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
            self._t = max(self._t, t)
            self.changed = True

    
    def _sort(self):
        idx_sorted = np.argsort(self._t_list[:self._idx])
        self._t_list[:self._idx] = self._t_list[idx_sorted]
        self._instr_list[:self._idx] = self._instr_list[idx_sorted]
        self._mask_list[:self._idx] = self._mask_list[idx_sorted]
        self._sorted = True


    def _add_sync_idle(self, t: int):
        self._add_instruction(t=t, cmd=BaseIoCmd.SYNC_IDLE, data=0, mask=0)
        
            
    def _get_instruction_list(self):
        if not self._sorted:
            self._sort()
        return self._instr_list[:self._idx]
    
    




