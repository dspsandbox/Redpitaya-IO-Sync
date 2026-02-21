from ..io.analog import AnalogIn, AnalogOut
from ..io.digital import DigitalIo
from ..io.pwm import Pwm
from ..io.scope import Scope
from ..io.sync import Sync 

class Rp_125_14_Mock():
    def __init__(self, ip: str, label: str):
        self._ip = ip
        self._label = label
        self._clk_freq = 125e6
        self._io_dict = {
            "analog_out_1": {"class": AnalogOut, "addr": 0x0},
            "analog_out_2": {"class": AnalogOut, "addr": 0x1},
            "analog_in_1": {"class": AnalogIn, "addr": 0x2},
            "analog_in_2": {"class": AnalogIn, "addr": 0x3},
            "digital_io_1": {"class": DigitalIo, "addr": 0x4},
            "digital_io_2": {"class": DigitalIo, "addr": 0x5},
            "pwm_1": {"class": Pwm, "addr": 0x6},
            "pwm_2": {"class": Pwm, "addr": 0x7},
            "pwm_3": {"class": Pwm, "addr": 0x8},
            "pwm_4": {"class": Pwm, "addr": 0x9},
            "scope_1": {"class": Scope, "addr": 0xA},    
            "scope_2": {"class": Scope, "addr": 0xB},
            "_sync": {"class": Sync, "addr": 0xC}
        }
        self._instr_ptr = 0
        self._frame_label_list = []
        self._en = 0

    def upload_bitstream(self, force=False):
        pass
    
        
    def reset(self):
        self.stop()
        self._instr_ptr = 0
        self._frame_label_list = []
    
    

    def add_frame(self, frame, label):
        instr_list = frame._get_instruction_list()
        instr_list_bytes = instr_list.tobytes()
        if self._instr_ptr + len(instr_list_bytes) > 0x10_0000:
            raise Exception(f"Instruction list exceeds instruction memory size of {0x10_0000} bytes.")
        self._instr_ptr += len(instr_list_bytes)
        self._frame_label_list.append(label)
        

    def _parse_err(self, err_code):
        io_name_list_with_err = []
        for io_name in self._io_dict.keys():
            io_addr = self._io_dict[io_name]["addr"]

            if err_code == (1 << io_addr):
                io_name_list_with_err.append(io_name)
        
        if len(io_name_list_with_err) == 0:
            return None
        else:
            return f"Error in IO(s): {', '.join(io_name_list_with_err)}"    
        

    def get_status(self):
        en = bool(self._en)
        sync_counter = en * (len(self._frame_label_list) - 1)

        err_code = 0
        done_code = en * 0xffffffff
        
        frame_label = self._frame_label_list[sync_counter] if sync_counter < len(self._frame_label_list) else None
        io_status = {}
        for io_name in self._io_dict.keys():
            if io_name[0] != "_":
                io_status[io_name] = {}
                io_status[io_name]["error"] = bool(err_code & (1 << self._io_dict[io_name]["addr"]))
                io_status[io_name]["done"] = bool(done_code & (1 << self._io_dict[io_name]["addr"]))

        err = any(io_status[io_name]["error"] for io_name in io_status.keys())
        if len(self._frame_label_list) == 0:
            completed = False
        else:
            completed = ((frame_label == self._frame_label_list[-1]) and 
                        all(io_status[io_name]["done"] for io_name in io_status.keys()) and 
                        not any(io_status[io_name]["error"] for io_name in io_status.keys()))
        status = {
            "enabled": en,
            "completed": completed,
            "error": err,
            "current_frame": frame_label,
            "io": io_status
        }
        return status


    def start(self):
        if len(self._frame_label_list) == 0:
            raise Exception("No frames uploaded. Please add at least one frame before starting the device.")
        pass
        
        status = self.get_status()
        if status["enabled"] and not status["completed"]:
            raise Exception("Device is already running. Please stop the device before starting it again.")
             
        self._en = 1


    def stop(self):
        self._en = 0

    
    def get_uid(self):
        uid = f"{self._label}@{self._ip}"
        return uid

    

