from redpitaya_io_sync.device.rp_125_14_mock import Rp_125_14_Mock
from redpitaya_io_sync.sequence import IoSequence
from redpitaya_io_sync.frame import IoSyncFrame, TriggerSource

from pprint import pprint


rp = Rp_125_14_Mock(ip="192.168.1.143", label="my_rp_125_14_mock")
seq = IoSequence()
fr = IoSyncFrame(device=rp, trig=TriggerSource.TrigImmediate, timeout=None)
fr.reset()

fr.analog_out_1.frequency(1e6)
fr.digital_io_1.tristate(val = 0, mask=0xffff)


# fr.analog_out_1.phase(90)
fr.analog_in_1.frequency(100e3)
# fr.analog_out_1.amplitude(t, val, update)
# fr.analog_out_2.amplitude(t, val, update)
# fr.analog_out_1.reset_phase(t, val, update)
# fr.analog_out_2.reset_phase(t, val, update)

# fr.analog_in_1.frequency(t, val, update)
# fr.analog_in_2.frequency(t, val, update)
# fr.analog_in_1.phase(t, val, update)
# fr.analog_in_2.phase(t, val, update)
# fr.analog_in_1.amplitude(t, val, update)
# fr.analog_in_2.amplitude(t, val, update)
# fr.analog_in_1.reset_phase(t, val, update)
# fr.analog_in_2.reset_phase(t, val, update)
# fr.analog_in_1.acquire(t, samples, dec, label)
# fr.analog_in_2.acquire(t, samples, dec, label)

fr.wait(0x1000000)
fr.pwm_1.duty_cycle(0.5)

for i in range(10):
    seq.add_frame(fr, label=f"my_frame_{i}")

seq.upload()
seq.start()
pprint(seq.get_status())

# fr.xadc.acquire(t, samples, dec, label)

# fr.digital.output(t, mask, val)
# fr.digital.tristate(t, mask, val)
# fr.digital.acquire(t, samples, dec, label)

# fr.monitor.source(t, val)
# fr.monitor.acquire(t, samples, dec, label)


# seq.reset()
# seq.append(fr, label)
# seq.replace(label, fr)

# rp.load(seq)
# rp.start()
# rp.stop()
# rp.get_status() 
# rp.get_data()