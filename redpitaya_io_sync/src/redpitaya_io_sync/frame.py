from unicodedata import name
import numpy as np

PREALLOCATION_BLOCK_LEN = 1024

class IoAddr:
    ANALOG_OUT_1 = 0x0
    ANALOG_OUT_2 = 0x1    
    ANALOG_IN_1 = 0x2
    ANALOG_IN_2 = 0x3
    DIGITAL_IO = 0x4
    PWM_1 = 0x5
    PWM_2 = 0x6
    PWM_3 = 0x7
    PWM_4 = 0x8
    SCOPE_1 = 0x9
    SCOPE_2 = 0xA
    SYNC = 0xF


class IoSyncFrame:
    def __init__(self, device):
        self._io_dict = {}
        for io_name in device.io_dict.keys():
            io_class = device.io_dict[io_name]["class"]
            io_addr = device.io_dict[io_name]["addr"]
            self._io_dict[io_name] = io_class(io_addr)
        
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
        for io in self._io_dict.values():
            io.reset()
        self._instr_list = np.zeros(PREALLOCATION_BLOCK_LEN, dtype=np.uint64)
        self._preallocation_len = PREALLOCATION_BLOCK_LEN

      
    def _has_changed(self):
        return any(io._has_changed() for io in self._io_dict.values())  
    
    def get_instruction_list(self):
        if not self._has_changed():
            return self._instr_list
        else:
            try:
                #Retrieve last instruction index for eaxch IO
                idx_max_dict = {} 
                for io_name in self._io_dict.keys():
                    idx_max_dict[io_name] = self._io_dict[io_name]._get_idx()

                #Sort instructions for each IO (if needed)
                for io in self._io_dict.values():
                    if io._has_changed():
                        io._sort_instructions()

                #Extend instructions
                for scope in [self.scope_1, self.scope_2]:
                    scope._acquire_tlast()

                for io in self._io_dict.values():
                    io._set_done()

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
                
                #Iterate over 

                


            except Exception as e:
                raise Exception(f"Error while retrieving instruction lists: {e}")
            
            finally:
                for io_name in self._io_dict.keys():
                    self._io_dict[io_name]._set_idx(idx_max_dict[io_name])
                    
                                




            
            


    


