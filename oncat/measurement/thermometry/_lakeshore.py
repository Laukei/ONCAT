from ._base import Thermometer

import pyvisa

class Model336(Thermometer):
	def __init__(self,**kwargs):
		super().__init__()
		rm = pyvisa.ResourceManager()
		self._t = rm.open_resource(kwargs.get('address'))
		self._t.read_termination = '\r\n'
		self._t.baud_rate = 57600
		self._t.data_bits = 7
		self._t.parity = pyvisa.constants.Parity.odd
		self._labels = {kwargs.get('labels')[0]:'A',
			kwargs.get('labels')[1]:'B',
			kwargs.get('labels')[2]:'C',
			kwargs.get('labels')[3]:'D'}


	def get(self,address=None):
		print(address)
		if address != None:
			return self._get(self._labels[address])
		else:
			print(self._labels)
			return {key:self._get(label) for key,label in self._labels.items()}

	def _get(self,address):
		return self._t.query('KRDG? {}'.format(self._labels[address]))