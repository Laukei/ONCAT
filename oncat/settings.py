import json

DEFAULT_SETTINGS = {
	'HW':{ # hardware settings
	},
	'SW':{ # software defaults
	}
}

class Settings:
	def __init__(self,filename='settings.json',**kwargs):
		'''
		kwargs: reset (bool) resets to factory settings
		'''
		self.filename = filename
		if kwargs.get('reset',False) is False:
			try:
				with open(self.filename,'r') as f:
					self._settings = json.loads(f.read())
			except IOError:
				self.reset_to_default()
		else:
			self.reset_to_default()


	def reset_to_default(self):
		self._settings = DEFAULT_SETTINGS


	def get(self,*keys):
		result = self._settings
		for key in keys:
			result = result[key]
		return result


	def set(self,keys,value):
		result = self._settings
		for key in keys[:-1]:
			result = result[key]
		result[keys[-1]] = value
		self.save()


	def save(self,filename=None):
		if not filename:
			filename = self.filename

		try:
			with open(filename,'w') as f:
				f.write(json.dumps(self._settings))
				return True
		except IOError:
			return False