import numpy as np
import copy
from .frame import IoSyncFrame, ParametrizedIoSyncFrame
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
        self._check_sequence_done()
        self._rsync_label_list = []
        for device in self._device_dict.values():
            device._reset()


    def add_frame(self, frame, device, label=None):
        self._check_sequence_done()
        if (type(frame) is not IoSyncFrame) and (type(frame) is not ParametrizedIoSyncFrame):
             raise Exception(f"Frame must be of type IoSyncFrame or ParametrizedIoSyncFrame, got {type(frame)}.") 
        if not issubclass(type(device), Rp_base):
                raise Exception(f"Provided device attribute is not a valid device instance.")
        if not isinstance(device, frame._device_type):
            raise Exception(f"Provided device ({device._get_uid()}) is not an instance of the frame device class ({frame._device_type.__name__}).")
        if device not in self._device_dict.values():
            raise Exception(f"Provided device ({device._get_uid()}) is not in the sequence device list.")        

        device._add_frame(frame, label)
        

    def add_rsync(self):
        self._check_sequence_done()
        label = f"rsync_{len(self._rsync_label_list)}"
        for device in self._device_dict.values():
            device._add_frame(IoSyncFrame(device_type=type(device), trig=TriggerSource._SYNC_DAISY_CHAIN), label=label)
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
            frame_label_dict[device_uid] = [(f"{label} (*)" if device._frame_dict[label]._trig in [TriggerSource.EXT_HIGH, TriggerSource.EXT_LOW, TriggerSource.EXT_RISE, TriggerSource.EXT_FALL, TriggerSource.EXT_RISE_FALL] else label) for label in device._frame_dict.keys()]
            

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
        description += "+" + ("-" * width_max + "+") * len(self._device_dict) + "\n"
        description += "NOTE: Frames with (*) are triggered by external trigger source.\n"
        
        return description

    def upload(self, force=False):
        self._check_sequence_done()
        for device in self._device_dict.values():
            device._upload(force=force)
                    

    def _check_sequence_done(self, autostop=True):
        status = self.get_status()
        done = all(device_status["done"] for device_status in status.values())
        enabled = any(device_status["enabled"] for device_status in status.values())
        if enabled and not done:
            raise Exception("Sequence is not finished, please stop it first")
        
        if enabled and done and autostop:
            self.stop()

    def start(self):
        self._check_sequence_done()
        for device in self._device_dict.values():
            device._start()




    def is_done(self):
        return all(device_status["done"] for device_status in self.get_status().values())
    
    def is_error(self):
        return any(device_status["error"] for device_status in self.get_status().values())

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
    
