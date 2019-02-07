import time
import threading
import logging

from ._base import Manager

TOLERANCE_DEFAULT = 1 #dB after which system realigns

logger = logging.getLogger(__name__)

class HoldManager(Manager):
	'''
	maximises measuerer moving mover
	'''
	def __init__(self,mover,measurer_function,**kwargs):
		super().__init__()
		self.mover = mover
		self._measurer_function = measurer_function
		self._sleeptime = kwargs.get('sleeptime',0.1)
		self._tolerance = kwargs.get('tolerance',TOLERANCE_DEFAULT)
		self._steps = None
		self._axes = kwargs.get('axes',('Xopt','Yopt'))
		self.active = False


	def run(self):
		self.movingthread = threading.Thread(target=self._run)
		self.movingthread.setDaemon(True)
		self.movingthread.start()


	def _run(self):
		self.active = True
		self._maxima = None
		self._stop = False
		while True:
			if self.check_for_end() == True:
				self.active = False
				return
			try:
				current_measurement = self.measure()
				if current_measurement < (self._maxima - self._tolerance) or current_measurement > (self._maxima + self._tolerance):
					self._realign()
				else:
					time.sleep(1)
			except TypeError:
				self._realign()


	def measure(self):
		return self._measurer_function()['opt']


	def _realign(self):
		axes = list(self._axes)
		data = {axis:[None,None,None] for axis in axes}
		movements = {axis:[] for axis in axes}
		steps = {}
		for axis in axes:
			self.mover.set_step(axis,100)
			steps[axis] = 100
			logger.info('start positions for HoldManager realignment on {}: {}'.format(axis,self.mover.get_position(axis)))
		while len(axes) > 0:
			for axis in axes:
				if self.check_for_end() == True:
					self.active = False
					return
				startpos = self.mover.get_position(axis)
				self.mover.move_down(axis)
				time.sleep(self._sleeptime)
				data[axis][0] = self.measure()
				for i in range(2):
					self.mover.move_up(axis)
					time.sleep(self._sleeptime)
					data[axis][1+i] = self.measure()
				if data[axis][1] == max(data[axis]):
					self.mover.move_down(axis)
					logger.info('found maxima for HoldManager realignment on {}: {}'.format(axis,self.mover.get_position(axis)))
					axes.pop(axes.index(axis))
					break
				elif data[axis][2] == max(data[axis]):
					self.mover.move_up(axis)
					time.sleep(self._sleeptime)
					movements[axis].append(1)
				elif data[axis][0] == max(data[axis]):
					for i in range(3):
						self.mover.move_down(axis)
						time.sleep(self._sleeptime)
					movements[axis].append(-1)
				if any(movement == 1 for movement in movements[axis]) and any(movement == -1 for movement in movements[axis]):
					logger.info('switched direction without finding maxima for {}, reducing step size'.format(axis))
					if steps[axis] > 1:
						steps[axis] = steps[axis] // 10
						if steps[axis] < 1:
							steps[axis] = 1
						self.mover.set_step(axis,steps[axis])
					else:
						logger.info('could not reduce step size any further, assuming at maxima')
						axes.pop(axes.index(axis))
		self._maxima = self.measure()



