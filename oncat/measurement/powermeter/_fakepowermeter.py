import random
import math

from ._base import PowerMeter

XOPT0 = 2.5
YOPT0 = 2.5
SIGMAXOPT = 0.05 / 2.3548
SIGMAYOPT = 0.05 / 2.3548
AMPLITUDE = 30

class FakePowerMeter(PowerMeter):
	def __init__(self,**kwargs):
		super().__init__()
		self._mover = kwargs.get('mover',None)
		self._power = random.gauss(-50,0.5)


	def _gaussian_power(self):
		if self._mover != None:
			Xopt = self._mover.get_position('Xopt')
			Yopt = self._mover.get_position('Yopt')
			Xside = ((Xopt - XOPT0)**2)/(2*(SIGMAXOPT**2))
			Yside = ((Yopt - YOPT0)**2)/(2*(SIGMAYOPT**2))
			inside = - (Xside + Yside)
			result = AMPLITUDE * (math.exp(inside))
		else:
			result = 0
		return result

	def get(self):
		return {'opt':self._power + self._gaussian_power() + random.gauss(0,0.01)}