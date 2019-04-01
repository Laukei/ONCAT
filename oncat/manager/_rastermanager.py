import time
import threading
import csv
import os

from ._base import Manager


class RasterManager(Manager):
	'''
	performs a raster scan with _mover taking _measurer_function at each point
	'''
	def __init__(self,mover,measurer_function,**kwargs):
		super().__init__()
		self.mover = mover
		self._measurer_function = measurer_function
		self.set_range(kwargs.get('range',None)) # format: (Xfrom, Xto, Yfrom, Yto)
		self._data = {'i':[],'j':[],'Xopt':[],'Yopt':[],'meas':[]}
		self._sleeptime = kwargs.get('sleeptime',0.1)
		self._signal = kwargs.get('signal',None)
		self._measurement_signal = kwargs.get('measurement_signal',None)
		self._autosavedirectory = kwargs.get('autosavedirectory','measurements')
		self.active = False


	def check_range(self):
		if self._range != None:
			assert len(self._range) == 4
			assert self._range[0] <= self._range[1]
			assert self._range[2] <= self._range[3]
		assert self.mover.can_move('Xopt',target=self._range[0]) == True
		assert self.mover.can_move('Xopt',target=self._range[1]) == True
		assert self.mover.can_move('Yopt',target=self._range[2]) == True
		assert self.mover.can_move('Yopt',target=self._range[3]) == True


	def get_data(self):
		return self._data


	def set_range(self,range_):
		self._range = range_


	def run(self):
		if self._range == None:
			raise ValueError
		else:
			self.check_range()
		self.movingthread = threading.Thread(target=self._run)
		self.movingthread.setDaemon(True)
		self.movingthread.start()


	def _run(self):
		self.active = True
		self._stop = False
		self._data = {'i':[],'j':[],'Xopt':[],'Yopt':[],'meas':[]}
		# home to Xfrom, Yfrom
		self.mover.move_to('Xopt',self._range[0],hold=True)
		self.mover.move_to('Yopt',self._range[2],hold=True)
		positionX = self.mover.get_position('Xopt')
		positionY = self.mover.get_position('Yopt')
		# measure, move
		total_X_steps = None
		current_X_step = 0
		current_Y_step = 0
		measurement_time = int(time.time())
		self._data_buffer = []

		def _write_buffer():
			os.makedirs(self._autosavedirectory, exist_ok=True)
			with open(os.path.join(self._autosavedirectory,'measurement_{}.txt'.format(measurement_time)),'a',newline='\n') as f:
				writer = csv.writer(f,delimiter='\t')
				writer.writerows(self._data_buffer)
				self._data_buffer = []

		while True:
			current_X_step = 0
			while True:
				time.sleep(self._sleeptime)
				if self.check_for_end() == True:
					self.active = False
					_write_buffer()
					return
				else:
					measurement = self._measurer_function()
					if self._measurement_signal:
						self._measurement_signal.emit(measurement)
					measurement = measurement.get('opt',None)

				positionX = self.mover.get_position('Xopt')
				positionY = self.mover.get_position('Yopt')
				self._data['i'].append(current_X_step)
				self._data['j'].append(current_Y_step)
				self._data['Xopt'].append(positionX)
				self._data['Yopt'].append(positionY)
				self._data['meas'].append(measurement)
				self._data_buffer.append([current_X_step,current_Y_step,positionX,positionY,measurement])
				if (total_X_steps == None and positionX >= self._range[1]) or (total_X_steps != None and current_X_step >= total_X_steps):
					break
				else:
					self.mover.move_up('Xopt')
					current_X_step += 1
			self.mover.move_to('Xopt',self._range[0],hold=True)
			_write_buffer()
			if positionY >= self._range[3]:
				break
			else:
				self.mover.move_up('Yopt')
				current_Y_step += 1 
				time.sleep(0.1)

		self.active = False
		if self._signal:
			self._signal.emit()