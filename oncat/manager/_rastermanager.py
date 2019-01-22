import time
import threading

from ._base import Manager


class RasterManager(Manager):
	'''
	performs a raster scan with _mover taking _measurer_function at each point
	'''
	def __init__(self,mover,measurer_function,movement_range,**kwargs):
		super().__init__()
		self._mover = mover
		self._measurer_function = measurer_function
		self._range = movement_range # format: (Xfrom, Xto, Yfrom, Yto)
		self._data = []
		self._sleeptime = kwargs.get('sleeptime',0.1)
		self._signal = kwargs.get('signal',None)
		assert self._range[0] <= self._range[1]
		assert self._range[2] <= self._range[3]


	def get_data(self):
		return self._data


	def run(self):
		self.movingthread = threading.Thread(target=self._run)
		self.movingthread.setDaemon(True)
		self.movingthread.start()


	def _run(self):
		# home to Xfrom, Yfrom
		self._mover.move_to('Xopt',self._range[0])
		self._mover.move_to('Yopt',self._range[2])
		positionX = self._mover.get_position('Xopt')
		positionY = self._mover.get_position('Yopt')
		# measure, move
		total_X_steps = None
		current_X_step = 0
		current_Y_step = 0
		while True:
			positionY = self._mover.get_position('Yopt')
			current_X_step = 0
			while True:
				time.sleep(self._sleeptime)
				if self.check_for_end() == True:
					return
				else:
					measurement = self.get_measurement().get('opt',None)

				positionX = self._mover.get_position('Xopt')
				self._data.append([current_X_step,current_Y_step,positionX,positionY,measurement])
				if (total_X_steps == None and positionX >= self._range[1]) or (total_X_steps != None and current_X_step >= total_X_steps):
					break
				else:
					self._mover.move_up('Xopt')
					current_X_step += 1
			self._mover.move_to('Xopt',self._range[0])
			if positionY >= self._range[3]:
				break
			else:
				self._mover.move_up('Yopt')
				current_Y_step += 1 
		if self._signal:
			self._signal.emit()


	def get_measurement(self):
		return self._measurer_function()