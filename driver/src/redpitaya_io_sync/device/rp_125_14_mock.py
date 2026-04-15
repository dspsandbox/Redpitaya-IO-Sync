import numpy as np
from .rp_125_14_z7010 import Rp_125_14_Z7010

np.random.seed(2)


class TcpCtrlClientMock():

    def write(self, addr, val):
        pass

    def read(self, addr, dtype=np.uint32, size=1):
        if size == 1:
            return 0
        else:
            return np.zeros(size, dtype=dtype)
    def load_bitstream(self, path, force=False):
        pass

    def add_mmap_region(self, addr, size):
        pass

class Rp_125_14_Mock(Rp_125_14_Z7010):
    def __init__(self, ip: str, label: str, force: bool = False):
        super().__init__(ip, label, force)
    
    def _init_tcp_ctrl_client(self):
        self._tcp_ctrl_client = TcpCtrlClientMock()
    
    def start(self):
        pass    
        
    def stop(self):
        pass

    def _init_dma(self):
        return
    
    def _get_compatible_devices(self):
        return []
   