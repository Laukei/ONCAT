import json

DEFAULT_SETTINGS = {
	'HW':{ # hardware settings
		'movement':{
			'FakeJanssen':{
				'executable':r'oncat\movement\janssen\fakecacli\cacli.exe',
				'lookup':json.dumps({'X':1,'Y':2}),
				'server':False,
				'verbose':False
			},
			'Janssen':{
				'executable':r'oncat\movement\janssen\cacli\cacli.exe',
				'lookup':json.dumps({'X':1,'Y':2}),
				'server':False,
				'verbose':False
			},
			'FakeANC350':{
				'lookup':json.dumps({'Xopt':1,'Yopt':2,'Z':3})
			},
			'ANC350':{
				'lookup':json.dumps({'Xopt':1,'Yopt':2,'Z':3})
			}
		}
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