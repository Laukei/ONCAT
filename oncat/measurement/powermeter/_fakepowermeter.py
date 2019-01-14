import random

from ._base import PowerMeter

class FakePowerMeter(PowerMeter):
	def __init__(self,**kwargs):
		super().__init__()
		self._power = random.gauss(-50,0.5)

	def get(self):
		return {'opt':self._power + random.gauss(0,0.1)}