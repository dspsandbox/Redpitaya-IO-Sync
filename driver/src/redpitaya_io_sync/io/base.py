
import numpy as np

class BaseIoCmd:
    NOP = 0xF
    DONE = 0xE



PREALLOCATION_BLOCK_LEN = 0x1000

class BaseIo():
    _requires_done_instruction = True #Whether the IO requires a DONE instruction at the end of the instruction list

    def __init__(self, addr, clk_freq):
        self._addr = addr
        self._clk_freq = clk_freq
        self._tlast = 0
        self._tnext = 0
        self._tdone=0
        self._t_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._idx = 0
        self._preallocation_len = PREALLOCATION_BLOCK_LEN
        self._locked = False
    
    
    def reset(self):
        self._tlast = 0
        self._tnext = 0
        self._tdone = 0
        self._t_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._idx = 0
        self._preallocation_len = PREALLOCATION_BLOCK_LEN
        self._locked = False

    def _add_instruction(self, cmd: int, data: int, duration: int = 1):
        if self._locked:
            raise Exception("Cannot add instruction because the instruction list is locked. Please reset instruction list.")
        #63 - 60 | 59 - 56 | 55 - 32 | 31 - 0
        #Addr    |   Cmd   |   Time  |   Data

        if cmd == BaseIoCmd.DONE:
            t = self._tdone
        else:
            t = self._tnext

        if (cmd != BaseIoCmd.DONE) and (t < self._tnext):
            raise Exception(f"Instruction time {t} is smaller than current time {self._tnext}.")
        
        if (cmd == BaseIoCmd.DONE) and (t < self._tdone):
            raise Exception(f"DONE instruction time {t} is smaller than current DONE time {self._tdone}.")

        #Insert NOP instructions every 2^24 clk cycles (if needed)
        while (t - self._tlast) > (1<<24):
            self._tnext = self._tlast + (1 << 24)
            self._add_instruction(cmd=BaseIoCmd.NOP, data=0, duration=(1 << 24))

        #Preallocate more space if needed
        if self._idx >= self._preallocation_len:
            self._instr_list = np.concatenate((self._instr_list, np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)))
            self._t_list = np.concatenate((self._t_list,  np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)))
            self._mask_list = np.concatenate((self._mask_list,  np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint32)))
            self._preallocation_len += PREALLOCATION_BLOCK_LEN

        #Create new instruction
        instr = ((self._addr << 60) | (cmd << 56) | ((t & 0xffffff) << 32) | data)
        
        #Add instruction to list
        self._instr_list[self._idx] = instr
        self._t_list[self._idx] = t
        self._idx += 1
        self._tlast = t
        self._tnext = t + duration
        self._tdone = t + duration
        return 

            
    def _get_instruction_and_time_list(self):
        
        if not self._locked:
            #Add DONE instruction at the end of the instruction list if required
            if self._requires_done_instruction:
                self._add_instruction(cmd=BaseIoCmd.DONE, data=0)
            
            #Set lock
            self._locked = True

        instr_list = self._instr_list[:self._idx]
        t_list = self._t_list[:self._idx]
        return instr_list, t_list
    
    def _get_time_list(self):
        return self._t_list[:self._idx]

    def get_time(self):
        return self._tnext

    def set_time(self, val: int):
        if val < self._tnext:
            raise Exception(f"Cannot set time to {val} because it is smaller than current time {self._tnext}.")
        self._tnext = val

    def wait(self, val: int = 0):
        t = self.get_time()
        self.set_time(t + val)

    def _is_locked(self):
        return self._locked
    



