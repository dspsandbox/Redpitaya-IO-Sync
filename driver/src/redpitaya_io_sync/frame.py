import numpy as np
from .io.sync import TriggerSource


PREALLOCATION_BLOCK_LEN = 0x10000

class IoSyncFrame:
    def __init__(self, device, trig=TriggerSource.TrigImmediate, timeout=None):
        self._device = device
        self._trig = trig
        self._timeout = timeout
        self._io_dict = {}
        self._idx = 0
        for io_name in self._device._io_dict.keys():
            io_class = self._device._io_dict[io_name]["class"]
            io_addr = self._device._io_dict[io_name]["addr"]
            clk_freq = self._device._clk_freq
            self._io_dict[io_name] = io_class(addr=io_addr, clk_freq=clk_freq)
        self._set_sync()
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._preallocation_len = PREALLOCATION_BLOCK_LEN    
        
        
    
    def __getattribute__(self, name):
        try:
            io = object.__getattribute__(self, "_io_dict")
        except AttributeError:
            return object.__getattribute__(self, name)

        if name in io:
            return io[name]
        return object.__getattribute__(self, name)

    def reset(self):
        """
        Reset all IOs and the frame instruction list.
        """
        for io in self._io_dict.values():
            io.reset()
        self._set_sync()
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._preallocation_len = PREALLOCATION_BLOCK_LEN
        self._idx = 0

    def _set_sync(self):
        self._io_dict["_sync"].trigger(src=self._trig, timeout=self._timeout)

    def _is_locked(self):
        return all(io._is_locked() for io in self._io_dict.values())  
    
    def _get_instruction_list(self):
        if self._is_locked():
            return self._instr_list[:self._idx]
        else:
            #Retrieve instruction lists and last instruction index for each IO  
            idx_max_dict = {}
            instr_list_dict = {}   
            t_list_dict = {}
            for io_name in self._io_dict.keys():
                instr_list, t_list = self._io_dict[io_name]._get_instruction_and_time_list()
                idx_max_dict[io_name] = len(instr_list)
                instr_list_dict[io_name] = instr_list
                t_list_dict[io_name] = t_list
            
            #Create dictionaries for iteration variables
            idx_dict = {}
            t_dict = {}
            for io_name in self._io_dict.keys():
                idx_dict[io_name] = 0
                t_dict[io_name] = 0
            
            
            #Iterate over instructions for all IOs in chronological order
            t = 0
            idx = 0
            keep_iterating = True
            while keep_iterating:
                keep_iterating = False
                
                if idx >= self._preallocation_len:
                    self._instr_list = np.concatenate((self._instr_list, np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)))
                    self._preallocation_len += PREALLOCATION_BLOCK_LEN
                
                for io_name in self._io_dict.keys():
                    io_idx = idx_dict[io_name]
                    io_idx_max = idx_max_dict[io_name]
                    if io_idx < io_idx_max:
                        keep_iterating = True
                        io_t = t_list_dict[io_name][io_idx]
                        io_t_previous = t_list_dict[io_name][io_idx - 1]
                        if (io_idx == 0) or (io_t_previous <= t):
                            self._instr_list[idx] = instr_list_dict[io_name][io_idx]
                            t_dict[io_name] = io_t
                            t = max(t, io_t)
                            idx_dict[io_name] += 1
                            idx += 1
            self._idx = idx
            return self._instr_list[:self._idx]

            
          
                
    def get_time(self):
        return max(io.get_time() for io_name, io in self._io_dict.items() if not io_name.startswith("_"))


    def set_time(self, val : int):
        for io_name, io in self._io_dict.items():
            if not io_name.startswith("_"):
                io.set_time(val)

    def wait(self, val : int = 0):
        t = self.get_time()
        self.set_time(t + val)


    def _get_acquisition_dict(self):
        acq_dict = {}
        for io_name in self._io_dict.keys():
            if "scope" in io_name:
                acq_dict[io_name] = self._io_dict[io_name]._get_acquisition_dict()
        return acq_dict





            
            


    


