import logging

import pyvisa

from ._base import PowerMeter

logger = logging.getLogger(__name__)

class ThorlabsPM100USB(PowerMeter):
	def __init__(self,**kwargs):
		super().__init__()
		rm = pyvisa.ResourceManager()
		self._device = rm.open_resource(kwargs.get('address'))
		self._device.read_termination = '\n'
		self._wavelength = kwargs.get('wavelength',1550)
		self._attenuation = kwargs.get('attenuation',0)
		self._averages = kwargs.get('averages',1)
		self._unit = kwargs.get('unit','DBM')
		idn = self._device.query('SYST:SENSOR:IDN?')
		logger.info('ThorlabsPM100USB sensor IDN: '.format(idn))
		self.set_defaults()


	def set_defaults(self):
		self._device.write('*RST') #reset to defaults
		self._device.write('SENS:CORR:WAV {}'.format(self._wavelength))
		self._device.write('SENS:CORR:LOSS:INP {}'.format(self._attenuation))
		self._device.write('SENS:AVER:COUN {}'.format(self._averages))
		self._device.write('SENS:POW:UNIT {}'.format(self._unit))
		self._device.write('SENS:POW:RANG:AUTO 1') #set auto-range


	def get(self):
		return {'opt':float(self._device.query('MEAS:POW?'))}