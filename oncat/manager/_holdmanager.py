import time
import threading

from ._base import Manager

DEFAULT_BOUNDS = 0.1 # in mm

class HoldManager(Manager):
	'''
	maximises measuerer moving mover

	needs a lookup table of distances, probably stored as JSON - could store in config or separately, in form:
	{'Xopt':
		-50
		-10
		-5
		-1
		1: {'voltage':n, 'frequency':m, 'steps':p},
		5: as above,
		10: as above,
		50: as above

		}
	'Yopt':
		as above}
	such that the algorithm can correctly set voltage/freq/steps in order to home to target accurately - the step
	sizes it uses when moving should be a fraction of the distance needed to correct the offset, to avoid overshooting
	'''
	def __init__(self,mover,measurer_function,**kwargs):
		super().__init__()
		self.mover = mover
		self._measurer_function = measurer_function
		self._sleeptime = kwargs.get('sleeptime',0.1)
		self.active = False
		self.calibration = kwargs.get('calibration',None)


	def _perform_calibration(self,axes=('Xopt','Yopt'),averages=1):
		'''
		!! DO NOT DO THIS WHEN HOLDING ALIGNMENT !!
		This will generate a calibration for the HoldManager

		** NOTE ** Doesn't work yet...
		'''
		self.calibration = {}
		for axis in axes:
			for move_direction in (self.mover.move_up,self.mover.move_down):
				movement = []
				voltage = []
				self.mover.set_static_amplitude(2)
				for v in range(1,70):
					start_pos = self.mover.get_position(axis)
					self.mover.set_voltage(axis,v)
					time.sleep(self._sleeptime)
					for i in range(averages):
						move_direction(axis)
						time.sleep(self._sleeptime)
					end_pos = self.mover.get_position(axis)
					print(start_pos-end_pos)
					movement.append((end_pos - start_pos)/averages)
					voltage.append(v)
			for row in zip(voltage,movement):
				print(row)


	def _scan_row(self,axis,steps,averages=1):
		start_position = self.mover.get_position(axis)
		assert type(steps) is int and steps >= 1
		for i in range(steps):
			self.mover.move_down(axis)
			time.sleep(self._sleeptime)
		measurements = []
		positions = []
		for i in range(int((steps*2) + 1)):
			positions.append(self.mover.get_position(axis))
			running_total = 0
			for j in range(averages):
				running_total += self._measurer_function()['opt']
			measurements.append(running_total/float(averages))
			self.mover.move_up(axis)
			time.sleep(self._sleeptime)
		self.mover.move_to(axis,start_position)
		return positions, measurements



	# def run(self):
	# 	if self._range == None:
	# 		raise ValueError
	# 	else:
	# 		self.check_range()
	# 	self.movingthread = threading.Thread(target=self._run)
	# 	self.movingthread.setDaemon(True)
	# 	self.movingthread.start()


	# def _run(self):
	# 	self.active = True
