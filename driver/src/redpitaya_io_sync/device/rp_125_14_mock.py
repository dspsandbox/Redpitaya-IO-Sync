import numpy as np
from .rp_125_14_z7010 import Rp_125_14_Z7010

np.random.seed(2)

class Rp_125_14_Mock(Rp_125_14_Z7010):
    def __init__(self, ip: str, label: str):
        super().__init__(ip, label)
    
    def _init_tcp_ctrl_client(self):
        pass

    def _write_mem(self, addr, data):
        pass

    def _read_mem(self, addr, dtype=np.uint32, size=1):
        if size == 1:
            return 0
        else:
            return np.zeros(size, dtype=dtype)

    def upload_bitstream(self, force=False):
        pass
    
    def start(self):
        pass    
        
    def stop(self):
        pass

    def _init_dma(self):
        return
   