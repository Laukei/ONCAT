import time
from ._base import BaseMonitor


class MoverPositionMonitor(BaseMonitor):
	'''
	position monitor for movers (typically Janssen or ANC350)
	'''
	def __init__(self,mover,lookup,**kwargs):
		super().__init__(**kwargs)
		self._mover = mover
		self._positions = {key:None for key in lookup.keys()}


	def _function(self):
		for key in self._positions.keys():
			self._positions[key] = self._mover.get_position(key)
		return self._positions

#	def _output(self,response):
#		print(response)
