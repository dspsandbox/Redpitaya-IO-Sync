import numpy as np
from io.sync import TriggerSource


PREALLOCATION_BLOCK_LEN = 0x10000

class IoSyncFrame:
    def __init__(self, device, trig=TriggerSource.TrigImmediate, timeout=None):
        self._device = device
        self._trig = trig
        self._timeout = timeout
        self._io_dict = {}
        for io_name in self.device._io_dict.keys():
            io_class = self.device._io_dict[io_name]["class"]
            io_addr = self.device._io_dict[io_name]["addr"]
            clk_freq = self.device._clk_freq
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

    def _set_sync(self):
        self._io_dict["_sync"].trigger(src=self._trig, timeout=self._timeout)

    def _is_locked(self):
        return all(io._is_locked() for io in self._io_dict.values())  
    
    def _get_instruction_list(self):
        if not self._is_locked():
            return self._instr_list
        else:
            try:
                #Retrieve last instruction index for each IO
                idx_max_dict = {} 
                for io_name in self._io_dict.keys():
                    idx_max_dict[io_name] = self._io_dict[io_name]._get_idx()

                #Extend instructions with DONE 
                for io in self._io_dict.values():
                    io._set_done()

                #Set IO lock (will unlocked if IO instructions change)
                for io in self._io_dict.values():
                    io._lock()

                #Retrieve extended instruction lists and last instruction index for each IO  
                idx_max_extended_dict = {}
                instr_list_extended_dict = {}   
                t_list_extended_dict = {}
                for io_name in self._io_dict.keys():
                    idx_max_extended_dict[io_name] = self._io_dict[io_name]._get_idx()
                    instr_list_extended_dict[io_name] = self._io_dict[io_name]._get_instruction_list()
                    t_list_extended_dict[io_name] = self._io_dict[io_name]._get_time_list()

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
                        io_idx_max = idx_max_extended_dict[io_name]
                        if io_idx < io_idx_max:
                            keep_iterating = True
                            io_t = t_list_extended_dict[io_name][io_idx]
                            io_t_previous = t_list_extended_dict[io_name][io_idx - 1]
                            if (io_idx == 0) or (io_t_previous <= t):
                                self._instr_list[idx] = instr_list_extended_dict[io_name][io_idx]
                                t_dict[io_name] = io_t
                                t = max(t, io_t)
                                idx_dict[io_name] += 1
                                idx += 1

                return self._instr_list[:idx]

            except Exception as e:
                raise Exception(f"Error while constructing frame instruction list: {e}")
            
            finally:
                #Rewind IO indices to their original values (before appending DONE instruction)
                for io_name in self._io_dict.keys():
                    self._io_dict[io_name]._set_idx(idx_max_dict[io_name])
                
                                




            
            


    


