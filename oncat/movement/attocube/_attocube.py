import random
import threading
import time

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
		self._range = {1:[0,5],2:[0,5],3:[0,5]}
		self.set_limits(kwargs.get('limits',{}))
		self._static_amp = kwargs.get('staticvoltage',2)


	def get_position(self,channel):
		return self._pos[self._lookup.get(channel,channel)] + ((random.random() - 0.5) * abs(2 - self._static_amp)) + (random.random()*0.01) if self._static_amp != 0 else -1

	def move_up(self,channel):
		self._move(channel,1)

	def move_down(self,channel):
		self._move(channel,-1)

	def move_to(self,channel,pos):
		self._pos[self._lookup.get(channel,channel)] = pos

	def set_limits(self,limits):
		self._limits = self._range
		for limit, value in limits.items():
			channel, limit_type = limit.split('_')
			self._limits[self._lookup.get(channel,channel)][0 if limit_type == 'min' else 1] = value

	def move_up_continuous(self,channel):
		self._moveContinuous(self._lookup.get(channel,channel),1)

	def move_down_continuous(self,channel):
		self._moveContinuous(self._lookup.get(channel,channel),-1)

	def stop(self,channel):
		self._stopMoving(self._lookup.get(channel,channel))

	def _moveContinuous(self,channel,direction):
		self.kill_thread = False
		def move_axis():
			i = 0
			while self.kill_thread != True:
				i+=1
				self._move(channel,direction)
				time.sleep(0.05)
		self.movingthread = threading.Thread(target=move_axis)
		self.movingthread.setDaemon(True)
		self.movingthread.start()

	def _move(self,channel,direction):
		axis = self._lookup.get(channel,channel)
		pos = self.get_position(axis)
		if (pos >= self._limits[axis][0] or direction == 1) and (pos <= self._limits[axis][1] or direction == -1):
			self._pos[axis] += direction*(self._freq[axis] * self._volt[axis] * self._step[axis]) * (1e-7)


	def _stopMoving(self,channel):
		self.kill_thread = True

	def set_voltage(self,channel,voltage):
		self._volt[self._lookup.get(channel,channel)] = voltage

	def set_frequency(self,channel,frequency):
		self._freq[self._lookup.get(channel,channel)] = frequency

	def set_step(self,channel,steps):
		self._step[self._lookup.get(channel,channel)] = steps

	def set_static_amplitude(self,static_amp):
		self._static_amp = static_amp