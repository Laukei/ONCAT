import random

from ._base import Thermometer

class FakeThermometer(Thermometer):
	def __init__(self,**kwargs):
		super().__init__()
		self._temperature = {kwargs.get('labels')[0]:random.gauss(1,0.1),
			kwargs.get('labels')[1]:random.gauss(4,0.3),
			kwargs.get('labels')[2]:random.gauss(10,1),
			kwargs.get('labels')[3]:random.gauss(50,5)}
			#self._labels = kwargs.get('labels')

	def get(self,address=None):
		if address != None:
			return self._temperature[address] + random.gauss(0,0.05)
		else:
			return {key:t+random.gauss(0,0.05) for key,t in self._temperature.items()}