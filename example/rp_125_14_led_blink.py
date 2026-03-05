from redpitaya_io_sync.device.rp_125_14_z7010 import Rp_125_14_Z7010
from redpitaya_io_sync.sequence import IoSequence
from redpitaya_io_sync.frame import IoSyncFrame, ParametrizedIoSyncFrame
from redpitaya_io_sync.io.scope import ScopeSource
from redpitaya_io_sync.io.sync import TriggerSource
import time


from pprint import pprint

rp0 = Rp_125_14_Z7010(ip="192.168.1.143", label="rp_0")



#Frames

fr_0 = IoSyncFrame(device_type=Rp_125_14_Z7010, trig=TriggerSource.EXT_HIGH)
fr_0.reset()
for i in range(256):
    fr_0.led.write(val=i)
    fr_0.wait(125e6/100)

fr_1 = ParametrizedIoSyncFrame(device_type=Rp_125_14_Z7010, trig=None)
def fr_1_func(frame, divider):
    for i in range(256):
        frame.led.write(val=i)
        frame.wait(125e6/divider)
fr_1.set_frame_function(fr_1_func)
fr_1.set_frame_parameter("divider", 100)

seq = IoSequence(device_list=[rp0])


# seq.add_frame(fr_0, label="fr_0", device=rp0)
# seq.add_rsync()
seq.add_frame(fr_1, label="fr_1", device=rp0)



for divider in [100, 50, 25]:
    fr_1.set_frame_parameter("divider", divider)
    seq.upload()

    t0 = time.time()
    seq.start()
    while not seq.is_done():
        time.sleep(1e-3)
    t1 = time.time()
    print(f"Sequence execution time: {t1-t0} seconds.")
    seq.stop()







