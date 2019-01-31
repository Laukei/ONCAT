from .thermometry import FakeThermometer, CTC100, Model336
from .powermeter import FakePowerMeter

def measurement_lookup(key=None):
	index = {
			'FakeThermometer':FakeThermometer,
			'CTC100':CTC100,
			'Model336':Model336,
			'FakePowerMeter':FakePowerMeter,
			 }
	if key == None:
		return index
	return index[key]

