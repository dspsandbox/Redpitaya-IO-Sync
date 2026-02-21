
import numpy as np

class BaseIoCmd:
    NOP = 0xF
    DONE = 0xE



PREALLOCATION_BLOCK_LEN = 0x1000

class BaseIo():
    def __init__(self, addr, clk_freq):
        self._addr = addr
        self._clk_freq = clk_freq
        self._tlast = 0
        self._tnext = 0
        self._t_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._idx = 0
        self._preallocation_len = PREALLOCATION_BLOCK_LEN
        self._sorted = True
        self._locked = False
    
    
    def reset(self):
        self._tlast = 0
        self._tnext = 0
        self._t_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._idx = 0
        self._preallocation_len = PREALLOCATION_BLOCK_LEN
        self._sorted = True
        self._locked = False


    def _add_instruction(self, cmd: int, data: int, duration: int = 1):
        #63 - 60 | 59 - 56 | 55 - 32 | 31 - 0
        #Addr    |   Cmd   |   Time  |   Data

        t = self._tnext

        if (cmd != BaseIoCmd.NOP) and (t < self._tnext):
            raise Exception(f"Instruction time {t} is smaller than current time {self._tnext}.")

        elif (cmd == BaseIoCmd.NOP) and (t <= self._tlast):
            raise Exception(f"NOP instruction time {t} is smaller or equal than last instruction time {self._tlast}.")
        

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
        self._locked = False
        return 
       

            
    def _get_instruction_and_time_list(self):
        #Sort instructions if not already sorted
        if not self._sorted:
            idx_sorted = np.argsort(self._t_list[:self._idx])
            self._t_list[:self._idx] = self._t_list[idx_sorted]
            self._instr_list[:self._idx] = self._instr_list[idx_sorted]
            self._sorted = True

        #Backup iteration variables
        idx = self._idx
        tlast = self._tlast
        tnext = self._tnext

        #Add DONE instruction at the end of the instruction list 
        self._add_instruction(cmd=BaseIoCmd.DONE, data=0)
        instr_list = self._instr_list[:self._idx]
        t_list = self._t_list[:self._idx]

        #Restore iteration variables
        self._idx = idx
        self._tlast = tlast
        self._tnext = tnext

        #Set lock
        self._locked = True

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




