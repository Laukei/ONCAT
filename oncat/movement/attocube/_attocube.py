import random

from .. import Mover


class ANC350(Mover):
	pass

class FakeANC350(Mover):
	def __init__(self,**kwargs):
		self._pos = {1:2.5, 2:2.5, 3:2.5}
		self._lookup = kwargs.get('lookup',{})
		self._freq = {1:100,2:100,3:100}
		self._volt = {1:30,2:30,3:30}
		self._step = {1:100,2:100,3:100}
		self._static_amp = 2


	def get_position(self,channel):
		return self._pos[self._lookup.get(channel,channel)] + ((random.random() - 0.5) * abs(2 - self._static_amp)) + (random.random()*0.01)

	def move_up(self,channel):
		self._pos[self._lookup.get(channel,channel)] += (self._freq[self._lookup.get(channel,channel)] * self._volt[self._lookup.get(channel,channel)] * self._step[self._lookup.get(channel,channel)]) * (1e-6)

	def move_down(self,channel):
		self._pos[self._lookup.get(channel,channel)] -= (self._freq[self._lookup.get(channel,channel)] * self._volt[self._lookup.get(channel,channel)] * self._step[self._lookup.get(channel,channel)]) * (1e-6)

	def move_to(self,channel,pos):
		self._pos[self._lookup.get(channel,channel)] = pos

	def set_voltage(self,channel,voltage):
		self._volt[self._lookup.get(channel,channel)] = voltage

	def set_frequency(self,channel,frequency):
		self._freq[self._lookup.get(channel,channel)] = frequency

	def set_step(self,channel,steps):
		self._step[self._lookup.get(channel,channel)] = steps

	def set_static_amplitude(self,static_amp):
		self._static_amp = static_amp