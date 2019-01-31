from ._base import Thermometer

import pyvisa

class CTC100(Thermometer):
	'''
	not needed so left incomplete
	'''
	def __init__(self,**kwargs):
		super().__init__()
		# rm = visa.ResourceManager()
		# self._t = rm.open_resource(kwargs.get('address'))
		# self._t.read_termination = '\r\n'
		# self._column_names = [header.strip() for header in self._t.ask('getOutput.names').split(',')]


	# def get(self,address=None):
	# 	datadict = {name:None for name in self._column_names}
	# 	names = [header.strip() for header in self._t.ask('getOutput.names').split(',')]
	# 	outputs = self._t.ask('getOutput').split(',')
	# 	for key, value in zip(names,outputs):
	# 		try:
	# 			datadict[key] = float(value)
	# 		except ValueError:
	# 			data.append(value)




	# 	if address != None:
	# 		return self._temperature[address] + random.gauss(0,0.05)
	# 	else:
	# 		return {key:t+random.gauss(0,0.05) for key,t in self._temperature.items()}