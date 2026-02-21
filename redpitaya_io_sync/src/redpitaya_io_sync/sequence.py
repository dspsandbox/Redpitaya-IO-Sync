import numpy as np
from .frame import IoSyncFrame


class IoSequence():
    def __init__(self):
        self._sequence_dict = {}
    
    def reset(self):
        self._sequence_dict = {}
        for device_uid in self._sequence_dict.keys():
            device = self._sequence_dict[device_uid]["device"]
            device.reset()

    def add_frame(self, frame, label=None):

        if type(frame) is not IoSyncFrame:
            raise Exception(f"Frame must be of type IoSyncFrame, got {type(frame)}.")
        
        
        
        device_uid = frame._device.get_uid()
        if device_uid not in self._sequence_dict:
            self._sequence_dict[device_uid] = {
                "device": frame._device, 
                "frames": {},
                }
        if label is None:
            label = f"frame_{len(self._sequence_dict[device_uid]['frames'])}"
        
        if label in self._sequence_dict[device_uid]["frames"]:
            raise Exception(f"Frame label {label} already exists in sequence for device {device_uid}.")
        
        
        self._sequence_dict[device_uid]["frames"][label] = frame


    def upload(self, force=False):
        """
        Upload frames to devices. Only uploads to devices that have at least one unlocked IO (with changed instructions) or if force=True.
        
        :param force: bool
        """

        for device_uid in self._sequence_dict.keys():
            device = self._sequence_dict[device_uid]["device"]
            if force or not all(io._is_locked() for io in self._sequence_dict[device_uid]["frames"].values()):
                device.reset()
                for label in self._sequence_dict[device_uid]["frames"].keys():
                    frame = self._sequence_dict[device_uid]["frames"][label]
                    device.add_frame(frame, label)
                


    def start(self):
        for device_uid in self._sequence_dict.keys():
            device = self._sequence_dict[device_uid]["device"]    
            device.start()

  

    def stop(self):
        for device_uid in self._sequence_dict.keys():
            device = self._sequence_dict[device_uid]["device"]    
            device.stop()
            

    def get_status(self):
        status_dict = {}
        for device_uid in self._sequence_dict.keys():
            device = self._sequence_dict[device_uid]["device"]    
            status_dict[device_uid] = device.get_status()
        return status_dict
        
        

    def get_scope():
        pass


        
    


    