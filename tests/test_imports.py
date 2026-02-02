from redpitaya_io_sync.devices import Rp_125_14_Z7010, Rp_125_14_Z7020, Rp_125_14_Mock
from redpitaya_io_sync.sequecer import IoSyncFrame, IoSequence
from redpitaya_io_sync.trigger import TrigHigh, TrigLow, TrigRise, TrigFall, TrigRiseFall

rp = Rp_125_14_Z7010(url="192.168.1.143")
seq = IoSequence()


sf = IoSyncFrame(trig=None)
sf.reset()

sf.analog_out_1.frequency(t, val, update)
sf.analog_out_1.phase(t, val, update)
sf.analog_out_2.phase(t, val, update)
sf.analog_out_1.amplitude(t, val, update)
sf.analog_out_2.amplitude(t, val, update)
sf.analog_out_1.reset_phase(t, val, update)
sf.analog_out_2.reset_phase(t, val, update)

sf.analog_in_1.frequency(t, val, update)
sf.analog_in_2.frequency(t, val, update)
sf.analog_in_1.phase(t, val, update)
sf.analog_in_2.phase(t, val, update)
sf.analog_in_1.amplitude(t, val, update)
sf.analog_in_2.amplitude(t, val, update)
sf.analog_in_1.reset_phase(t, val, update)
sf.analog_in_2.reset_phase(t, val, update)
sf.analog_in_1.acquire(t, samples, dec, label)
sf.analog_in_2.acquire(t, samples, dec, label)

sf.pwm.duty_cycle(t, mask, val)

sf.xadc.acquire(t, samples, dec, label)

sf.digital.output(t, mask, val)
sf.digital.tristate(t, mask, val)
sf.digital.acquire(t, samples, dec, label)

sf.monitor.source(t, val)
sf.monitor.acquire(t, samples, dec, label)


seq.reset()
seq.append(sf, label)
seq.replace(label, sf)

rp.load(seq)
rp.start()
rp.stop()
rp.get_status() 
rp.get_data()