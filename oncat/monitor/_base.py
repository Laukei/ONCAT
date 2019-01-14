import time


class BaseMonitor:
	'''
	basic general-purpose monitor.

	executes `function`
	with `parameters`
	every `sleeptime`
	returning response via `signal`
	'''
	def __init__(self,**kwargs):
		self._func = kwargs.get('function')
		self._params = kwargs.get('parameters',{})
		self._st = kwargs.get('sleeptime',1)
		self._sig = kwargs.get('signal')

	def run(self):
		'''
		does _function
		returns via _output
		'''
		while True:
			response = self._function()
			self._output(response)
			time.sleep(self._st)

	def _function(self):
		if self._func:
			return self._func(*self._params.get('args',[]),**self._params.get('kwargs',{}))
		else:
			return None

	def _output(self, response):
		if self._sig:
			self._sig.emit(response)