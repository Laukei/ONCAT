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
		self._settings = {
			'X':{
				'frequency':None,
				'temperature':None,
				'steps':None,
				'step_size':None
			},
			'Y':{
				'frequency':None,
				'temperature':None,
				'steps':None,
				'step_size':None
			}
		}
		self._function_lookup = {
			'frequency':self._m.set_frequency,
			'temperature':self._m.set_temperature,
			'steps':self._m.set_steps,
			'step_size':self._m.set_step_size
		}


	def get_position(self,channel):
		return self._m.get_position(self._lookup.get(channel,channel))

	def move_up(self,channel):
		self._m.move(self._lookup.get(channel,channel),FORWARD)

	def move_down(self,channel):
		self._m.move(self._lookup.get(channel,channel),BACKWARD)

	def set_frequency(self,channel,frequency):
		self._setter('frequency',channel,frequency)

	def set_temperature(self,channel,temperature):
		self._setter('temperature',channel,temperature)
		
	def set_steps(self,channel,steps):
		self._setter('steps',channel,steps)
		
	def set_step_size(self,channel,step_size):
		self._setter('step_size',channel,step_size)

	def _setter(self,name,channel,value):
		if self._settings[channel][name] != value:
			self._function_lookup[name](self._lookup.get(channel,channel),value)
			self._settings[channel][name] = value

	def set_settings(self,bundle):
		for setting, [value, axes] in bundle.items():
			for axis in axes:
				self._setter(setting,axis,value)




class FakeJanssen(Janssen):
	'''
	due to existence of fakecacli.exe this is literally just a copy of Janssen() kept separate for semantics
	'''
	pass