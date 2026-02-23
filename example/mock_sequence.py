from redpitaya_io_sync.device.rp_125_14_mock import Rp_125_14_Mock
from redpitaya_io_sync.sequence import IoSequence
from redpitaya_io_sync.frame import IoSyncFrame, TriggerSource
from redpitaya_io_sync.io.scope import ScopeSource

from pprint import pprint

#Device
rp = Rp_125_14_Mock(ip="192.168.1.143", label="my_rp_125_14_mock")

#Frame
fr = IoSyncFrame(device=rp, trig=TriggerSource.TrigImmediate, timeout=None)
fr.reset()
fr.analog_out_1.frequency(1e6)
fr.digital_io_1.tristate(val = 0, mask=0xf)
fr.analog_out_1.phase(90)
fr.wait(500)
fr.pwm_1.duty_cycle(0.5)
fr.scope_1.source(ScopeSource.ANALOG_IN_1)
fr.scope_2.source(ScopeSource.ANALOG_IN_2)
fr.scope_1.acquire(label="my_acq_1", samples=8, dec=1)
fr.scope_2.acquire(samples=8, dec=1)

#Sequence
seq = IoSequence()
for i in range(4):
    seq.add_frame(fr, label=f"frame_iter_{i}")

seq.update(force=False)
seq.start()

#Print status
print("STATUS:")
pprint(seq.get_status())


#Print status
print("SCOPE:")
pprint(seq.get_scope())

