import numpy as np
from io.analog import AnalogIn, AnalogOut
from io.digital import DigitalIo
from io.pwm import Pwm
from io.scope import Scope
from io.sync import Sync


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
    def __init__(self):
        self.analog_out_1 = AnalogOut(IoAddr.ANALOG_OUT_1)
        self.analog_out_2 = AnalogOut(IoAddr.ANALOG_OUT_2)
        self.analog_in_1 = AnalogIn(IoAddr.ANALOG_IN_1)
        self.analog_in_2 = AnalogIn(IoAddr.ANALOG_IN_2)
        self.digital_io = DigitalIo(IoAddr.DIGITAL_IO)
        self.pwm_1 = Pwm(IoAddr.PWM_1)
        self.pwm_2 = Pwm(IoAddr.PWM_2)
        self.pwm_3 = Pwm(IoAddr.PWM_3)
        self.pwm_4 = Pwm(IoAddr.PWM_4)
        self.scope_1 = Scope(IoAddr.SCOPE_1)
        self.scope_2 = Scope(IoAddr.SCOPE_2)
        self.sync = Sync(IoAddr.SYNC)

        #Helper dictionary to access Io objects by name
        self._io_dict = {
            "analog_out_1": self.analog_out_1,
            "analog_out_2": self.analog_out_2,
            "analog_in_1": self.analog_in_1,
            "analog_in_2": self.analog_in_2,
            "digital_io": self.digital_io,
            "pwm_1": self.pwm_1,
            "pwm_2": self.pwm_2,
            "pwm_3": self.pwm_3,
            "pwm_4": self.pwm_4,
            "scope_1": self.scope_1,
            "scope_2": self.scope_2,
            "sync": self.sync
        }

      
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
                


            except Exception as e:
                raise Exception(f"Error while retrieving instruction lists: {e}")
            
            finally:
                for io_name in self._io_dict.keys():
                    self._io_dict[io_name]._set_idx(idx_max_dict[io_name])
                    
                                




            
            


    


