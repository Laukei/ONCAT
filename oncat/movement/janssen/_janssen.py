import time
import logging

from pyjanssen import MCM, FORWARD, BACKWARD
from pyjanssen.janssen_mcm import CacliError

from .. import Mover

logger = logging.getLogger(__name__)

LIMITS = {
	'frequency':[int,0,600],
	'temperature':[int,0,300],
	'steps':[int,0,1000],
	'step_size':[int,0,100]
}

class Janssen(Mover):
	LIMITS = LIMITS
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
		for i in range(10):
			try:
				return self._m.get_position(self._lookup.get(channel,channel))
			except (IndexError,CacliError) as e:
				logger.warning('error reading position ({}/5): {}'.format(channel,i+1,e))
				time.sleep(0.1)
		raise CacliError('Unable to speak to cacli.exe')

	@staticmethod
	def get_limits():
		return LIMITS

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