import time
import numpy as np
from zynq_tcp_ctrl import ZynqTcpCtrlClient
from ..frame import IoSyncFrame



class Rp_base():
    def __init__(self, ip: str, label: str):
        self._ip = ip
        self._label = label
        self._check_attribute("_clk_freq")
        self._check_attribute("_io_dict")
        self._check_attribute("_mmap_dict")
        self._check_attribute("_addr_dict")
        self._check_attribute("_bitstream")

        self._ptr_dict = {}
        self._init_ptr()
        self._tcp_ctrl_client = None
        self._init_tcp_ctrl_client()
        self.upload_bitstream(force=False)
        self.stop()
        
    def _init_tcp_ctrl_client(self):
        self._tcp_ctrl_client = ZynqTcpCtrlClient(self._ip)

    def _init_ptr(self):
        self._ptr_dict["instr"] = self._mmap_dict["mem_instr"]["addr"]
        for io_name in self._io_dict.keys():
            if "scope" in io_name:
                self._ptr_dict[io_name] = self._mmap_dict[f"mem_{io_name}"]["addr"]


    def _check_attribute(self, attr):
        if not hasattr(self, attr):
            raise Exception(f"Attribute {attr} not found. Please define {attr} in the device subclass.")

    def upload_bitstream(self, force=False):
        self._tcp_ctrl_client.upload_bitstream(bitstream_path=self._bitstream, force=force)
        
    def reset(self):
        self.stop()
        self._frame_dict = {}
        self._init_ptr()
    

    def add_frame(self, frame, label=None):
        if type(frame) != IoSyncFrame:
            raise Exception(f"Frame must be of type IoSyncFrame. Got {type(frame)}.")

        if label is None:
            label = f"frame_{len(self._frame_dict)}"

        instr_list = frame._get_instruction_list()
        
        #Check instruction memory size
        instr_list_bytes = instr_list.tobytes()
        instr_list_size = len(instr_list_bytes)
        if self._ptr_dict["instr"] + instr_list_size > self._mmap_dict["mem_instr"]["addr"] + self._mmap_dict["mem_instr"]["size"]:
            raise Exception(f"Frame exceeds total instruction memory size of {self._mmap_dict['mem_instr']['size']} bytes.")
        
        #Check scope memory size
        acq_dict = frame._get_acquisition_dict()
        for scope_label in acq_dict.keys():
            for acq_label in acq_dict[scope_label].keys():
                acq_samples = acq_dict[scope_label][acq_label]["samples"]
                acq_size = acq_samples * np.int16().nbytes  
                if (self._ptr_dict[scope_label] + acq_size) > (self._mmap_dict[f"mem_{scope_label}"]["addr"] + self._mmap_dict[f"mem_{scope_label}"]["size"]):
                    raise Exception(f"Frame exceeds total {scope_label} memory size of {self._mmap_dict[f'mem_{scope_label}']['size']} bytes.")
        
        #Append frame
        self._write_mem(addr=self._ptr_dict["instr"], data=instr_list_bytes)

        #Append frame metadata
        self._frame_dict[label] = frame
        self._ptr_dict["instr"] += instr_list_size
        for scope_label in acq_dict.keys():
            for acq_label in acq_dict[scope_label].keys():
                acq_dict[scope_label][acq_label]["addr"] = self._ptr_dict[scope_label]
                self._ptr_dict[scope_label] += acq_dict[scope_label][acq_label]["samples"] * np.int16().nbytes 
            
    def update(self, force=False):
        frame_dict = self._frame_dict
        if force or not all(frame._is_locked() for frame in self._frame_dict.values()):      
            self.reset()
            for label in frame_dict.keys():
                frame = frame_dict[label]
                self.add_frame(frame=frame, label=label)


        

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
        en = bool(self._read_mem(addr=self._addr_dict["reg_bank_en"]))
        sync_counter = self._read_mem(addr=self._addr_dict["reg_bank_sync_counter"])
        err_code = bool(self._read_mem(addr=self._addr_dict["reg_bank_err"]))
        done_code = bool(self._read_mem(addr=self._addr_dict["reg_bank_done"]))
        frame_label_list = list(self._frame_dict.keys())
        frame_label = frame_label_list[sync_counter] if sync_counter < len(frame_label_list) else None
        io_status = {}
        for io_name in self._io_dict.keys():
            if io_name[0] != "_":
                io_status[io_name] = {}
                io_status[io_name]["error"] = bool(err_code & (1 << self._io_dict[io_name]["addr"]))
                io_status[io_name]["done"] = bool(done_code & (1 << self._io_dict[io_name]["addr"]))

        err = any(io_status[io_name]["error"] for io_name in io_status.keys())
        if len(frame_label_list) == 0:
            completed = False
        else:
            completed = ((frame_label == frame_label_list[-1]) and 
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
        if len(self._frame_dict) == 0:
            raise Exception("No frames uploaded. Please add at least one frame before starting the device.")
        pass
        
        status = self.get_status()
        if status["enabled"] and not status["completed"]:
            raise Exception("Device is already running. Please stop the device before starting it again.")
             
        
        #configure DMAs
        #assert enable bit

        

    def stop(self):
        #reset DMAs
        #deassert enable bit
        #flush fifos
        return


    
    def get_uid(self):
        uid = f"{self._label}@{self._ip}"
        return uid

    def _write_mem(self, addr, data):
        self._tcp_ctrl_client.write(addr=addr, data=data)   

    def _read_mem(self, addr, dtype=np.uint32, size=1):
        return self._tcp_ctrl_client.read(addr=addr, dtype=dtype, size=size)

    def get_scope(self):
        scope_dict = {}
        for frame_label in self._frame_dict.keys():
            scope_dict[frame_label] = {}
            frame = self._frame_dict[frame_label]
            acq_dict = frame._get_acquisition_dict()
            
            for scope_label in acq_dict.keys():
                scope_dict[frame_label][scope_label] = {}
                for acq_label in acq_dict[scope_label].keys():
                    addr = acq_dict[scope_label][acq_label]["addr"]
                    samples = acq_dict[scope_label][acq_label]["samples"]
                    t = acq_dict[scope_label][acq_label]["t"]
                    dec = acq_dict[scope_label][acq_label]["dec"]
                    data = self._read_mem(addr=addr, size=(samples), dtype=np.int16)
                    scope_dict[frame_label] [scope_label][acq_label] = {"t": t, "dec": dec, "samples": samples, "data": data}
        return scope_dict