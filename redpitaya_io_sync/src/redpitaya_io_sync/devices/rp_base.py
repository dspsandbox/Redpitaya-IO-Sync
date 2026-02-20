from zynq_tcp_ctrl import ZynqTcpCtrlClient
import time



class Rp_base():
    def __init__(self, ip: str, label: str):
        self._ip = ip
        self._label = label
        self._check_attribute("_clk_freq")
        self._check_attribute("_io_dict")
        self._check_attribute("_mmap_range_dict")
        self._check_attribute("_addr_dict")
        self._check_attribute("_bitstream")

        self._instr_ptr = self._addr_dict["dma_instr"]["addr"]
        self._frame_label_list = []
        self._tcp_ctrl_client = ZynqTcpCtrlClient(self.ip)
        self.upload_bitstream(force=False)
        self.stop()


    def _check_attribute(self, attr):
        if not hasattr(self, attr):
            raise Exception(f"Attribute {attr} not found. Please define {attr} in the device subclass.")

    def upload_bitstream(self, force=False):
        self._tcp_ctrl_client.upload_bitstream(bitstream_path=self._bitstream, force=force)
        
    def reset(self):
        self.stop()
        self._instr_ptr = self._addr_dict["dma_instr"]["addr"]
        self._frame_label_list = []
    
    

    def add_frame(self, frame, label):
        instr_list = frame._get_instruction_list()
        instr_list_bytes = instr_list.tobytes()
        if self._instr_ptr + len(instr_list_bytes) > self._addr_dict["dma_instr"]["addr"] + self._addr_dict["dma_instr"]["size"]:
            raise Exception(f"Instruction list exceeds instruction memory size of {self._addr_dict['dma_instr']['size']} bytes.")
        self._tcp_ctrl_client.write(addr=self._instr_ptr, data=instr_list_bytes)
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
        en = bool(self._tcp_ctrl_client.read(addr=self._addr_dict["reg_bank_en"], size=4))
        sync_counter = self._tcp_ctrl_client.read(addr=self._addr_dict["reg_bank_sync_counter"], size=4)
        err_code = bool(self._tcp_ctrl_client.read(addr=self._addr_dict["reg_bank_err"], size=4))
        done_code = bool(self._tcp_ctrl_client.read(addr=self._addr_dict["reg_bank_done"], size=4))
        
        frame_label = self._frame_label_list[sync_counter] if sync_counter < len(self._frame_label_list) else None
        io_status = {}
        for io_name in self._io_dict.keys():
            if io_name[0] != "_":
                io_status[io_name] = {}
                io_status[io_name]["error"] = bool(err_code & (1 << self._io_dict[io_name]["addr"]))
                io_status[io_name]["done"] = bool(done_code & (1 << self._io_dict[io_name]["addr"]))

        err = any(io_status[io_name]["error"] for io_name in io_status.keys())
        if len(self._frame_label_list) == 0:
            finished = False
        else:
            finished = ((frame_label == self._frame_label_list[-1]) and 
                        all(io_status[io_name]["done"] for io_name in io_status.keys()) and 
                        not any(io_status[io_name]["error"] for io_name in io_status.keys()))
        status = {
            "enabled": en,
            "finished": finished,
            "error": err,
            "frame": frame_label,
            "io": io_status
        }
        return status


    def start(self):
        if len(self._frame_label_list) == 0:
            raise Exception("No frames uploaded. Please add at least one frame before starting the device.")
        pass
        
        status = self.get_status()
        if status["enabled"] and not status["finished"]:
            raise Exception("Device is already running. Please stop the device before starting it again.")
             
        
        #configure DMAs
        #assert enable bit

        

    def stop(self):
        #reset DMAs
        #deassert enable bit
        #flush fifos
        return



    
    def get_uid(self):
        uid = f"{self.label}@{self.ip}"
        return uid

    
