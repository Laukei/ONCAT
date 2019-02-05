from .thermometry import FakeThermometer, CTC100, Model336
from .powermeter import FakePowerMeter, ThorlabsPM100USB

def measurement_lookup(key=None):
	index = {
			'FakeThermometer':FakeThermometer,
			'CTC100':CTC100,
			'Model336':Model336,
			'FakePowerMeter':FakePowerMeter,
			'ThorlabsPM100USB':ThorlabsPM100USB
			 }
	if key == None:
		return index
	return index[key]

