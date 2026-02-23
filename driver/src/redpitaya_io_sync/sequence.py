import numpy as np
import copy
from .frame import IoSyncFrame


class IoSequence():
    def __init__(self):
        self._device_dict = {}
    
    
    def reset(self):
        self._device_dict = {}


    def add_frame(self, frame, label=None):
        if type(frame) is not IoSyncFrame:
            raise Exception(f"Frame must be of type IoSyncFrame, got {type(frame)}.")       
        device = frame._device
        device_uid = frame._device.get_uid()
        if device_uid not in self._device_dict:
            device.reset()
            self._device_dict[device_uid] = device
        device.add_frame(frame, label)       
        

    def update(self, force=False):
        for device in self._device_dict.values():
            device.update(force=force)
                    

    def start(self):
        for device in self._device_dict.values():
            device.start()

  

    def stop(self):
        for device in self._device_dict.values():
            device.stop()
            

    def get_status(self):
        status_dict = {}
        for device_uid, device in self._device_dict.items():
            status_dict[device_uid] = device.get_status()
        return status_dict


    def get_scope(self):
        scope_dict = {}
        for device_uid, device in self._device_dict.items():
            scope_dict[device_uid] = device.get_scope()
        return scope_dict     