import numpy as np
import copy
from .frame import IoSyncFrame
from .io.sync import TriggerSource
from .device.rp_base import Rp_base


class IoSequence():
    def __init__(self, device_list):
        self._rsync_label_list= []
        self._device_dict = {}
        for device in device_list:
            device_uid = device._get_uid()
            if device_uid in self._device_dict:
                raise Exception(f"Device {device_uid} already exists in sequence. Please make sure all devices in the device list have unique UIDs.")
            self._device_dict[device_uid] = device
            
    
    
    def reset(self):
        self._rsync_label_list = []
        self._device_dict = {}


    def add_frame(self, frame, label=None, device=None):
        if type(frame) is not IoSyncFrame:
            raise Exception(f"Frame must be of type IoSyncFrame, got {type(frame)}.")       
        
        if device is None and not isinstance(frame._device, Rp_base):
            raise Exception(f"Please provide a valid device instance or make sure the device attribute of the frame is a valid device instance.")
        if device is not None and not isinstance(device, Rp_base):
            raise Exception(f"Provided device ({device}) is not a valid device instance.")
        if device is not None and isinstance(frame._device, Rp_base) and device._get_uid() != frame._device._get_uid():
            raise Exception(f"Provided device ({device._get_uid()}) does not match the device in the frame instance ({frame._device._get_uid()}). If you trying to add the same frame on multiple devices, please use a non-instantiated device class as device attribute for your frame.")
        if device is not None and isinstance(device, Rp_base) and device._get_uid() not in self._device_dict:
            raise Exception(f"Device ({device._get_uid()}) not found in sequence. Please add the device to the device_list attribute when initializing the sequence.")
        if device is None and isinstance(frame._device, Rp_base) and frame._device._get_uid() not in self._device_dict:
            raise Exception(f"Frame instance's device ({frame._device._get_uid()}) not found in sequence. Please add the device to the device_list attribute when initializing the sequence.")
        if device is not None and issubclass(frame._device, Rp_base) and not isinstance(device, frame._device):
            raise Exception(f"Provided device ({device._get_uid()}) is not an instance of the frame device class ({frame._device.__name__}).")
        

        if device is None:
            device = frame._device
        device._add_frame(frame, label)
        

    def add_rsync(self):
        label = f"rsync_{len(self._rsync_label_list)}"
        for device in self._device_dict.values():
            device._add_frame(IoSyncFrame(device=device, trig=TriggerSource.SYNC_DAISY_CHAIN), label=label)
        self._rsync_label_list.append(label)


    def sequence_description(self):      
        width_max = 0
        for device_uid in self._device_dict.keys():
            device = self._device_dict[device_uid]
            width = max(len(frame_label) for frame_label in device._frame_dict.keys()) if len(device._frame_dict) > 0 else 0
            width_max = max([width_max, width, len(device_uid)])
        
        padding = 1
        width_max += 2*padding
        description = ""
        description += "+"  +("-" * width_max + "+") * len(self._device_dict) + "\n"
        device_uid_list = list(self._device_dict.keys())
        for i in range(len(device_uid_list)):
            device_uid = device_uid_list[i]
            device = self._device_dict[device_uid]
            description += "|"
            description += " " * padding
            description += device_uid
            description += (width_max - len(device_uid) - padding) * " "
        description += "|"
        description += "\n"
        description += "+" + ("-" * width_max + "+") * len(self._device_dict) + "\n"
        
        
        idx_dict = {}
        idx_dict["rsync"] = 0

        frame_label_dict = {}
        for device_uid in self._device_dict.keys():
            device = self._device_dict[device_uid]
            frame_label_dict[device_uid] = [(f"{label} (*)" if device._frame_dict[label]._trig is not 0 
                                            and label not in self._rsync_label_list else label) for label in device._frame_dict.keys()]
            

        for rsync_label in self._rsync_label_list:
            idx_rsync_max = max(frame_label_list.index(rsync_label) for frame_label_list in frame_label_dict.values())
            for device_uid in self._device_dict.keys():
                idx_sync = frame_label_dict[device_uid].index(rsync_label)
                for i in range(idx_rsync_max - idx_sync):
                    frame_label_dict[device_uid].insert(idx_sync, "")
        
        description_len = max(len(frame_label_dict[device_uid]) for device_uid in frame_label_dict.keys())
        
        for i in range(description_len):
            description += "|"
            for device_uid in frame_label_dict.keys():

                labels = frame_label_dict[device_uid]
                if i < len(labels):
                    label = labels[i]
                else:
                    label = ""
                if label in self._rsync_label_list:
                    padding_char = "-"
                    separator_char = "-"
                else:
                    padding_char = " "
                    separator_char = "|"
                description += padding_char * padding
                description += label
                description += (width_max - len(label) - padding) * padding_char
                if device_uid != list(frame_label_dict.keys())[-1]:
                    description += separator_char
                
            
            description += "|"
            description += "\n"
        description += "+" + ("-" * width_max + "+") * len(self._device_dict) 
        
        return description

    def upload(self, force=False):
        for device in self._device_dict.values():
            device._upload(force=force)
                    

    def start(self):
        for device in self._device_dict.values():
            device._start()

  

    def stop(self):
        for device in self._device_dict.values():
            device._stop()
            

    def get_status(self):
        status_dict = {}
        for device_uid, device in self._device_dict.items():
            status_dict[device_uid] = device._get_status()
        return status_dict


    def get_scope(self):
        scope_dict = {}
        for device_uid, device in self._device_dict.items():
            scope_dict[device_uid] = device._get_scope()
        return scope_dict     