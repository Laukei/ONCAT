from ._base import Mover
from .janssen import FakeJanssen, Janssen
from .attocube import FakeANC350, ANC350

def lookup(key=None):
	index = {
			'FakeJanssen':FakeJanssen,
			'FakeANC350':FakeANC350,
			'ANC350':ANC350,
			'Janssen':Janssen,
			 }
	if key == None:
		return index
	return index[key]