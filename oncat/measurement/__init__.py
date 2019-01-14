from .thermometry import FakeThermometer
from .powermeter import FakePowerMeter

def measurement_lookup(key=None):
	index = {
			'FakeThermometer':FakeThermometer,
			'FakePowerMeter':FakePowerMeter
			 }
	if key == None:
		return index
	return index[key]

