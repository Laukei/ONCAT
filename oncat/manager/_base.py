class Manager:
	'''
	generic Manager class for subclassing, implementing generic Manager behaviours
	'''
	def __init__(self,*args,**kwargs):
		self._stop = False


	def stop(self):
		self._stop = True
		self.active = False


	def check_for_end(self):
		if self._stop:
			return True