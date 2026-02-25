from redpitaya_io_sync.device.rp_125_14_mock import Rp_125_14_Mock
from redpitaya_io_sync.device.rp_125_14_z7020 import Rp_125_14_Z7020
from redpitaya_io_sync.sequence import IoSequence
from redpitaya_io_sync.frame import IoSyncFrame
from redpitaya_io_sync.io.scope import ScopeSource
from redpitaya_io_sync.io.sync import TriggerSource



from pprint import pprint

rp0 = Rp_125_14_Mock(ip="192.168.1.143", label="rp_0")
rp1 = Rp_125_14_Mock(ip="192.168.1.144", label="rp_1")
rp2 = Rp_125_14_Mock(ip="192.168.1.145", label="rp_2")


#Frames
fr_0_0 = IoSyncFrame(device=rp0, trig=TriggerSource.EXT_HIGH)
fr_0_1 = IoSyncFrame(device=rp0, trig=None)
fr_0_2 = IoSyncFrame(device=rp0, trig=None)

fr_1_0 = IoSyncFrame(device=rp1, trig=None)
fr_1_1 = IoSyncFrame(device=rp1, trig=None)

fr_2_0 = IoSyncFrame(device=rp2, trig=None)
fr_2_1 = IoSyncFrame(device=rp2, trig=None)
fr_2_2 = IoSyncFrame(device=rp2, trig=None)

#Instructions (only on frame_0_0 for testing)
fr_0_0.reset()
fr_0_0.analog_out_1.frequency(1e6)
fr_0_0.digital_io_1.tristate(val = 0, mask=0xf)
fr_0_0.analog_out_1.phase(90)
fr_0_0.wait(500)
fr_0_0.pwm_1.duty_cycle(0.5)
fr_0_0.scope_1.source(ScopeSource.ANALOG_IN_1)
fr_0_0.scope_2.source(ScopeSource.ANALOG_IN_2)
fr_0_0.scope_1.acquire(label="my_acq_1", samples=8, dec=1)
fr_0_0.scope_2.acquire(samples=8, dec=1)


#Sequence
seq = IoSequence(device_list=[rp0, rp1, rp2])

seq.add_frame(fr_0_0, label="fr_0_0")
seq.add_rsync()
seq.add_frame(fr_0_1, label="fr_0_1")
seq.add_frame(fr_0_2, label="fr_0_2")
seq.add_frame(fr_1_0, label="fr_1_0")
seq.add_frame(fr_1_1, label="fr_1_1")
seq.add_frame(fr_2_0, label="fr_2_0")
seq.add_frame(fr_2_1, label="fr_2_1")
seq.add_rsync()
seq.add_frame(fr_2_2, label="fr_2_2")


seq.upload(force=False)
seq.start()

#Print status
print("STATUS:")
pprint(seq.get_status())


#Print status
print("SCOPE:")
pprint(seq.get_scope())



print("SEQUENCE DESCRIPTION:")
print(seq.sequence_description())
