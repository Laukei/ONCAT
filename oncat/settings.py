import json

DEFAULT_SETTINGS = {
	'HW':{ # hardware settings
		'FakeJanssen':{
			'executable':r'oncat\movement\janssen\fakecacli\cacli.exe',
			'lookup':{'X':1,'Y':2},
			'server':False,
			'verbose':False
		},
		'Janssen':{
			'executable':r'oncat\movement\janssen\cacli\cacli.exe',
			'lookup':{'X':1,'Y':2},
			'server':False,
			'verbose':False
		},
		'FakeANC350':{
			'lookup':{'Xopt':1,'Yopt':2,'Z':3}
		},
		'ANC350':{
			'lookup':{'Xopt':1,'Yopt':2,'Z':3}
		},
		'FakeThermometer':{
		},
		'FakePowerMeter':{
		}
	},
	'SW':{ # software defaults
		'longrangemover':{
			'device':'FakeJanssen',
			'sleeptime':0.5
			},
		'shortrangemover':{
			'device':'FakeANC350',
			'sleeptime':0.25,
			'limits': {'Yopt_max':3.3}
			},
		'vgroovecontrol':{
			'voltage':30,
			'frequency':100
		},
		'zcontrol':{
			'voltage':40,
			'frequency':100,
			'lockstate':False
		},
		'probecontrol':{
			'temperature':293,
			'temperature-auto':True,
			'frequency':100, #Hz, 0-600
			'steps':100, 
			'power':100 #step size
		},
		'global':{
			'staticvoltage':0, #start with 0 voltage to prevent heating on startup
			'probeautotempsensor':'T1',
			'triggerbackedoffmessage':False
		},
		'ctc100':{
			'device':'FakeThermometer',
			'sleeptime':0.5,
			'labels':['T1','T2','T3','T4']
		},
		'lakeshore':{
			'device':'FakeThermometer',
			'sleeptime':0.5,
			'labels':['T5','T6','T7','T8']
		},
		'thorlabspowermeter':{
			'device':'FakePowerMeter',
			'sleeptime':0.5
		}
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


	def get_plaintext(self):
		return json.dumps(self._settings,indent=2,sort_keys=True)

	def get_defaults(self):
		return json.dumps(DEFAULT_SETTINGS)

	def set_plaintext(self,text):
		try:
			self._settings = json.loads(text)
			self.save()
		except json.decoder.JSONDecodeError:
			print('error converting settings to json')


	def save(self,filename=None):
		if not filename:
			filename = self.filename
		try:
			with open(filename,'w') as f:
				f.write(json.dumps(self._settings))
				return True
		except IOError:
			return False