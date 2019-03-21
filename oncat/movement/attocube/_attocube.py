import random
import threading
import time

from pyanc350.v2 import Positioner

from .. import Mover

LIMITS = {
	'frequency':[int,0,1000],
	'voltage':[int,0,70],
	'steps':[int,0,1000],
	'static_amplitude':[float,0,2]
}

class ANC350(Mover):
	LIMITS = LIMITS
	def __init__(self,**kwargs):
		self._p = Positioner()
		self._last_positions = {0:None,1:None,2:None}
		self._lookup = kwargs.get('lookup',{})
		self._range = {0:[0,5],1:[0,5],2:[0,5]}
		self.set_limits(kwargs.get('limits',{}))
		self._static_amp = kwargs.get('staticvoltage',0)
		self.set_static_amplitude(self._static_amp)
		self._settings = {
			'Xopt': {
				'frequency':self._p.getFrequency(self.lookup('Xopt')),
				'voltage':self._p.getAmplitude(self.lookup('Xopt')),
				'step':None,
			},
			'Yopt': {
				'frequency':self._p.getFrequency(self.lookup('Yopt')),
				'voltage':self._p.getAmplitude(self.lookup('Yopt')),
				'step':None,
			},
			'Z': {
				'frequency':self._p.getFrequency(self.lookup('Z')),
				'voltage':self._p.getAmplitude(self.lookup('Z')),
				'step':None,
			}
		}
		self._function_lookup = {
			'frequency':self._p.frequency,
			'voltage':self._p.amplitude,
			'step':self._p.stepCount
		}

	@staticmethod
	def get_limits():
		return LIMITS

	def lookup(self,channel):
		return self._lookup.get(channel,channel)

	def get_position(self,channel):
		position = self._p.getPosition(self.lookup(channel)) / 1000000.0
		self._last_positions[self.lookup(channel)] = position
		return position

	def move_up(self,channel):
		if self.can_move(channel,direction=0):
			self._p.moveSingleStep(self.lookup(channel),0)

	def move_down(self,channel):
		if self.can_move(channel,direction=0):
			self._p.moveSingleStep(self.lookup(channel),1)

	def move_to(self,channel,pos):
		target = int(pos*1000000)
		if self.can_move(channel,target=target):
			self._p.moveAbsolute(self.lookup(channel),target)
			print('moving!')

	def set_limits(self,limits):
		self._limits = self._range
		for limit, value in limits.items():
			channel, limit_type = limit.split('_')
			self._limits[self._lookup.get(channel,channel)][0 if limit_type == 'min' else 1] = value

	def move_up_continuous(self,channel):
		if self.can_move(channel,direction=0):
			self._p.moveContinuous(self.lookup(channel),0)

	def move_down_continuous(self,channel):
		if self.can_move(channel,direction=1):
			self._p.moveContinuous(self.lookup(channel),1)

	def stop(self,channel):
		self._p.stopApproach(self.lookup(channel))
		print('stopped')

	def can_move(self,channel,**kwargs):
		axis = self.lookup(channel)
		pos = self._last_positions[axis]
		direction = kwargs.get('direction',None)
		target = kwargs.get('target',None)
		if target is not None:
			target = target / 1000000.0
		if self._static_amp == 0:
			return False
		elif direction != None and ((pos >= self._limits[axis][0] or direction == 0) and (pos <= self._limits[axis][1] or direction == 1)):
			return True
		elif target != None and target >= self._limits[axis][0] and target <= self._limits[axis][1]:
			return True
		else:
			return False

	def set_voltage(self,channel,voltage):
		self._setter('voltage',channel,voltage)

	def set_frequency(self,channel,frequency):
		self._setter('frequency',channel,frequency)

	def set_step(self,channel,step):
		self._setter('step',channel,step)

	def set_static_amplitude(self,static_amp):
		self._static_amp = static_amp
		self._p.staticAmplitude(int(static_amp*1000))

	def _setter(self,name,channel,value):
		if self._settings[channel][name] != value:
			self._function_lookup[name](self.lookup(channel),int(value*1000))
			self._settings[channel][name] = value

	def set_settings(self,bundle):
		for setting, [value, axes] in bundle.items():
			for axis in axes:
				self._setter(setting,axis,value)


class FakeANC350(Mover):
	LIMITS = LIMITS
	def __init__(self,**kwargs):
		self._pos = {1:2.5, 2:2.5, 3:2.5}
		self._lookup = kwargs.get('lookup',{})
		self._freq = {1:100,2:100,3:100}
		self._volt = {1:30,2:30,3:30}
		self._step = {1:100,2:100,3:100}
		self._range = {1:[0,5],2:[0,5],3:[0,5]}
		self.set_limits(kwargs.get('limits',{}))
		self._static_amp = kwargs.get('staticvoltage',2)
		self._settings_index = {
			'frequency':self._freq,
			'voltage':self._volt,
			'step':self._step
		}

	@staticmethod
	def get_limits():
		return LIMITS

	def get_position(self,channel):
		return self._pos[self._lookup.get(channel,channel)] + ((random.random() - 0.5) * abs(2 - self._static_amp)) + (random.random()*0.0001) if self._static_amp != 0 else -1

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

	def can_move(self,channel,**kwargs):
		axis = self._lookup.get(channel,channel)
		pos = self._pos[axis]
		direction = kwargs.get('direction',None)
		target = kwargs.get('target',None)
		if self._static_amp == 0:
			return False
		elif direction != None and ((pos >= self._limits[axis][0] or direction == 1) and (pos <= self._limits[axis][1] or direction == -1)):
			return True
		elif target != None and target >= self._limits[axis][0] and target <= self._limits[axis][1]:
			return True
		else:
			return False

	def _moveContinuous(self,channel,direction):
		self.kill_thread = False
		def move_axis():
			i = 0
			while self.kill_thread != True:
				i+=1
				self._move(channel,direction)
				time.sleep(1/self._freq[self._lookup.get(channel,channel)])
		self.movingthread = threading.Thread(target=move_axis)
		self.movingthread.setDaemon(True)
		self.movingthread.start()

	def _move(self,channel,direction):
		axis = self._lookup.get(channel,channel)
		pos = self.get_position(axis)
		if (pos >= self._limits[axis][0] or direction == 1) and (pos <= self._limits[axis][1] or direction == -1):
			self._pos[axis] += direction*(self._volt[axis] * self._step[axis]) * (1e-6)


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

	def _setter(self,name,channel,value):
		self._settings_index[name][self._lookup.get(channel,channel)] = value

	def set_settings(self,bundle):
		for setting, [value, axes] in bundle.items():
			for axis in axes:
				self._setter(setting,axis,value)