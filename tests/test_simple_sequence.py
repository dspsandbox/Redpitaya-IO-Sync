from redpitaya_io_sync.device.rp_125_14_mock import Rp_125_14_Mock
from redpitaya_io_sync.sequence import IoSequence
from redpitaya_io_sync.frame import IoSyncFrame, TriggerSource

from pprint import pprint

#Device
rp = Rp_125_14_Mock(ip="192.168.1.143", label="my_rp_125_14_mock")

#Frame
fr = IoSyncFrame(device=rp, trig=TriggerSource.TrigImmediate, timeout=None)
fr.reset()
fr.analog_out_1.frequency(1e6)
fr.digital_io_1.tristate(val = 0, mask=0xffff)
fr.analog_in_1.frequency(100e3)
fr.wait(0x1000000)
fr.pwm_1.duty_cycle(0.5)

#Sequence
seq = IoSequence()
for i in range(10):
    seq.add_frame(fr, label=f"my_frame_{i}")
seq.upload()
seq.start()

#Print status
pprint(seq.get_status())

