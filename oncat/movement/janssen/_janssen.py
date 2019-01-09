from .. import Mover
from pyjanssen import MCM, FORWARD, BACKWARD


class Janssen(Mover):
	def __init__(self,**kwargs):
		self._m = MCM(
			exe=kwargs.get('executable','.'),
			verbose=kwargs.get('verbose',False),
			server=kwargs.get('server',False)
		)
		self._lookup = kwargs.get('lookup',{})


	def get_position(self,channel):
		return self._m.get_position(self._lookup.get(channel,channel))

	def move_up(self,channel):
		self._m.move(self._lookup.get(channel,channel),FORWARD)

	def move_down(self,channel):
		self._m.move(self._lookup.get(channel,channel),BACKWARD)

	def set_frequency(self,channel,frequency):
		self._m.set_frequency(self._lookup.get(channel,channel),frequency)

	def set_temperature(self,channel,temperature):
		self._m.set_temperature(self._lookup.get(channel,channel),temperature)
		
	def set_steps(self,channel,steps):
		self._m.set_steps(self._lookup.get(channel,channel),steps)
		
	def set_step_size(self,channel,step_size):
		self._m.set_step_size(self._lookup.get(channel,channel),step_size)


class FakeJanssen(Janssen):
	'''
	due to existence of fakecacli.exe this is literally just a copy of Janssen() kept separate for semantics
	'''
	pass