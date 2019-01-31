from ._base import Thermometer

import pyvisa

class Model336(Thermometer):
	def __init__(self,**kwargs):
		super().__init__()
		rm = visa.ResourceManager()
		self._t = rm.open_resource(kwargs.get('address'))
		self._t.read_termination = '\r\n'
		self._t.baud_rate = 57600
		self._t.data_bits = 7
		self._t.parity = pyvisa.constants.Parity.odd
		

