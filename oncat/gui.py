import sys
import copy
import logging

from PyQt5 import QtGui, QtCore, QtWidgets #QtWebEngineWidgets
from PyQt5.uic import loadUi
from pyjanssen.janssen_mcm import CacliError
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from .settings import Settings
from .settingsgui import SettingsDialog
from .diagram import Diagram, Scan
from .monitor import launch_monitor_as_thread, MoverPositionMonitor, BaseMonitor
from .movement import movement_lookup
from .measurement import measurement_lookup
from .manager import RasterManager, HoldManager

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		loadUi('oncat/ui/mainwindow.ui',self)
		self.name_of_application = "ONCAT Optoelectronic Nanopositioner Control & Alignment Toolkit"
		self.setWindowTitle(self.name_of_application)

		self._devices = {}
		self._managers = {}
		self._threads = {}
		self._thread_pause_flags = {}
		self._currently_moving = []

		self._settings = Settings()
		self.link_settings()
		self.populate_default_settings()

		self.add_stretches()

		self.instantiate_hardware()
		self.instantiate_managers()
		self.generate_helpers()
		self.connect_interface()
		self.add_validators()

		self.add_diagrams()
		self.connect_timers()

		self.connect_menubar()
		self.set_lock(False)

		self.final_setup()
		self.show()


	def instantiate_managers(self):
		self._managers['rastermanager'] = RasterManager(self._devices['shortrangemover'],self._devices['powermeter'].get,
				signal=self.scanFinished,autosavedirectory=self._settings.get('SW','global','autosavedirectory'),
				measurement_signal=self.updateMeasurement)
		self._managers['holdmanager'] = HoldManager(self._devices['shortrangemover'],self._devices['powermeter'].get)


	def connect_menubar(self):
		self.actionSettings.triggered.connect(self.open_settings)


	@QtCore.pyqtSlot()
	def open_settings(self):
		self.settings_window = SettingsDialog(self._settings)
		self.settings_window.exec_()


	def link_settings(self):
		self._settingsgroup = {
			self.vgroove_frequency: 	(int,str,('SW','vgroovecontrol','frequency')),
			self.vgroove_voltage: 		(int,str,('SW','vgroovecontrol','voltage')),
			self.z_voltage: 			(int,str,('SW','zcontrol','voltage')),
			self.z_frequency: 			(int,str,('SW','zcontrol','frequency')),
			self.z_lock: 				(bool,bool,('SW','zcontrol','lockstate')),
			self.probe_temp_auto: 		(bool,bool,('SW','probecontrol','temperature-auto')),
			self.probe_temp: 			(int,str,('SW','probecontrol','temperature')),
			self.probe_frequency: 		(int,str,('SW','probecontrol','frequency')),
			self.probe_power: 			(int,str,('SW','probecontrol','power')),
			self.probe_power_slider: 	(int,int,('SW','probecontrol','power')),
			self.probe_steps: 			(int,str,('SW','probecontrol','steps')),
			self.global_voltage: 		(float,str,('SW','global','staticvoltage')),
			self.from_Xopt: 			(float,str,('SW','scansettings','xoptfrom')),
			self.to_Xopt: 				(float,str,('SW','scansettings','xoptto')),
			self.from_Yopt: 			(float,str,('SW','scansettings','yoptfrom')),
			self.to_Yopt: 				(float,str,('SW','scansettings','yoptto'))
			}
		self._measurementgroup = {
			'T1':self.global_temp1,
			'T2':self.global_temp2,
			'T3':self.global_temp3,
			'T4':self.global_temp4,
			'T5':self.global_temp5,
			'T6':self.global_temp6,
			'T7':self.global_temp7,
			'T8':self.global_temp8,
			'opt':self.global_opticalpower}
		self.lockgroup = {'probecontrol':{True:self.probe_locked.show,
										False:self.probe_locked.hide},
							'zcontrol':{True:self.z_locked.show,
										False:self.z_locked.hide}
			}


	def final_setup(self):
		self._going_to = {'Xopt':False, 'Yopt':False}
		self.on_zlock_change(self._settings.get('SW','zcontrol','lockstate'))
		self.on_probe_temp_auto(self.probe_temp_auto.checkState())
		self.set_current_diagram(0)
		self.graphsTabWidget.currentChanged.connect(self.set_current_diagram)


	@QtCore.pyqtSlot(int)
	def set_current_diagram(self,index_):
		self._active_diagram = self._diagrams[index_]
		self.canvas = self._canvases[index_]
		self.fig = self._figs[index_]


	def set_lock(self,state=True,controlset=None):
		if controlset != None:
			self.lockgroup[controlset][state]()
		else:
			for key in self.lockgroup:
				self.lockgroup[key][state]()



	def populate_default_settings(self):
		for i, (widget, (fromtype, totype, location)) in enumerate(self._settingsgroup.items()):
			if type(widget) == QtWidgets.QLineEdit:
				def _store_setting(widget=widget,loc=location,fromtype=fromtype):
					new_text = widget.text()
					try:
						new_text = fromtype(new_text)
					except ValueError:
						pass	
					self._settings.set(loc,new_text)
				widget.editingFinished.connect(_store_setting)
				widget.setText(totype(self._settings.get(*location)))
			elif type(widget) == QtWidgets.QCheckBox:
				def _store_setting(state,loc=location):
					self._settings.set(loc,True if state != 0 else False)
				widget.stateChanged.connect(_store_setting)
				widget.setChecked(self._settings.get(*location))
			elif type(widget) == QtWidgets.QSlider:
				def _store_setting(value,loc=location):
						self._settings.set(loc,value)
				widget.valueChanged.connect(_store_setting)
				widget.setValue(self._settings.get(*location))
			elif type(widget) == QtWidgets.QDoubleSpinBox:
				def _store_setting(widget=widget,loc=location,fromtype=fromtype):
					new_value = widget.value()
					try:
						new_value = fromtype(new_value)
					except ValueError:
						pass	
					self._settings.set(loc,new_value)
				widget.editingFinished.connect(_store_setting)
				widget.setValue(self._settings.get(*location))


	def add_stretches(self):
		self.horizontalLayoutTop.addStretch(1)
		self.leftMenuLayout.addStretch(1)


	def instantiate_hardware(self):
		for monitor in ('longrangemover','shortrangemover','thermometer1','thermometer2','powermeter'):
			self._instantiate_hardware(monitor)


	def _instantiate_hardware(self,identifier):
		if identifier == 'longrangemover':
			self._spin_mover('longrangemover')
		elif identifier == 'shortrangemover':
			self._spin_mover('shortrangemover',staticvoltage=self._settings.get('SW','global','staticvoltage'))
		elif identifier in ('thermometer1','thermometer2','powermeter'):
			self._spin_measurer(identifier,mover=self._devices['shortrangemover'])
		else:
			raise ValueError


	def _spin_mover(self,identifier,**kwargs):
		selected_class = self._settings.get('SW',identifier,'device')
		self._devices[identifier] = movement_lookup(selected_class)(
									**self._settings.get('HW',selected_class),
									**self._settings.get('SW',identifier),
									**kwargs)
		self._thread_pause_flags[identifier] = {'pause':False}
		self._threads[identifier] = launch_monitor_as_thread(self._devices[identifier],
															 self._settings.get('HW',selected_class,'lookup'),
															 monitor=MoverPositionMonitor,
															 signal=self.updatePositions,
															 pause_flag = self._thread_pause_flags[identifier],
															 sleeptime=self._settings.get('SW',identifier,'sleeptime'))


	def _spin_measurer(self,identifier,**kwargs):
		selected_class = self._settings.get('SW',identifier,'device')
		self._devices[identifier] = measurement_lookup(selected_class)(
									**self._settings.get('HW',selected_class),
									**self._settings.get('SW',identifier),
									**kwargs)
		self._thread_pause_flags[identifier] = {'pause':False}
		self._threads[identifier] = launch_monitor_as_thread(monitor=BaseMonitor,
															 function=self._devices[identifier].get,
															 signal=self.updateMeasurement,
															 pause_flag = self._thread_pause_flags[identifier],
															 sleeptime=self._settings.get('SW',identifier,'sleeptime'))


	@QtCore.pyqtSlot(dict)
	def on_update_measurement(self,values):
		for key,value in values.items():
			self._measurementgroup[key].setText(str(round(value,4)))


	def add_diagrams(self):
		self._canvases = []
		self._figs = []
		self._diagrams = []
		for diagram, name in ((Diagram,'Diagram'), (Scan,'Scan')):
			self._diagrams.append(diagram(limits=self._settings.get('SW','shortrangemover','limits')))
			self._canvases.append(self._diagrams[-1].canvas())
			self._figs.append(self._diagrams[-1].fig())
			widget = QtWidgets.QWidget()
			layout = QtWidgets.QVBoxLayout()
			layout.addWidget(self._canvases[-1])
			layout.addWidget(NavigationToolbar(self._canvases[-1],self))
			widget.setLayout(layout)
			self.graphsTabWidget.addTab(widget, name)
			self._canvases[-1].setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding))
			self._figs[-1].tight_layout()
			self._canvases[-1].draw_idle()


	def connect_timers(self):
		self._vctimer = QtCore.QTimer()
		self._vctimer.timeout.connect(self._static_voltage_change)
		self._vctimer.setSingleShot(True)

		self._movertimer = QtCore.QTimer()
		self._movertimer.timeout.connect(self._longrangemove)

		self._graphtimer = QtCore.QTimer()
		self._graphtimer.timeout.connect(self._update_graphs)
		self._graphtimer.start(self._settings.get('SW','global','graphupdaterate'))


	def connect_interface(self):
		self.updatePositions.connect(self.on_update_positions)
		self.updateMeasurement.connect(self.on_update_measurement)
		self.global_voltage.valueChanged.connect(self.on_static_voltage_change)
		self.probe_temp_auto.stateChanged.connect(self.on_probe_temp_auto)
		self.probe_power.textEdited.connect(self.on_probecontrol_powerchange)
		self.probe_power_slider.valueChanged.connect(self.on_probecontrol_powerchange)
		self.z_lock.stateChanged.connect(self.on_zlock_change)
		self.button_goto.clicked.connect(self.on_goto_clicked)
		self.button_scan.clicked.connect(self.on_scan_clicked)
		self.button_scan_reset.clicked.connect(self.on_scan_reset_clicked)
		self.button_hold.clicked.connect(self.on_hold_clicked)
		self.scanFinished.connect(self.on_scan_finished)
		self.gotoFinished.connect(self._goto_reset)

		for button in self.probe_buttongroup:
			button.pressed.connect(self.on_longrangemover_pressed)
			button.released.connect(self.on_longrangemover_released)

		for button in self.shortrangemover_buttongroup:
			button.pressed.connect(self.on_shortrangemover_pressed)
			button.released.connect(self.on_shortrangemover_released)


	@QtCore.pyqtSlot(int)
	def on_zlock_change(self,val):
		for widget in [self.z_voltage,self.z_frequency,
					   self.button_up_Z,self.button_down_Z,
					   self.button_up_X,self.button_down_X,
					   self.button_up_Y,self.button_down_Y]:
			if val == 0: #if False (val is 3-state)
				#widget.setReadOnly(False)
				widget.setEnabled(True)
			else:
				#widget.setReadOnly(True)
				widget.setEnabled(False)
				self._settings.set(('SW','global','triggerbackedoffmessage'),True)


	@QtCore.pyqtSlot(int)
	@QtCore.pyqtSlot(str)
	def on_probecontrol_powerchange(self,value):
		if type(value) == str:
			try:
				self.probe_power_slider.setValue(int(value))
			except ValueError:
				pass
		elif type(value) == int:
			self.probe_power.setText(str(value))


	def generate_helpers(self):
		self.probe_buttongroup = { # links long range movement button with mover move functions
			self.button_up_X:		[self._devices['longrangemover'].move_up,'X'],
			self.button_down_X:		[self._devices['longrangemover'].move_down,'X'],
			self.button_up_Y:		[self._devices['longrangemover'].move_up,'Y'],
			self.button_down_Y:		[self._devices['longrangemover'].move_down,'Y']
		}
		self.z_buttongroup = {
			self.button_up_Z:		[self._devices['shortrangemover'].move_up_continuous,'Z'],
			self.button_down_Z:		[self._devices['shortrangemover'].move_down_continuous,'Z']
		}
		self.vgroove_buttongroup = {
			self.button_up_Xopt:	[self._devices['shortrangemover'].move_up_continuous,'Xopt'],
			self.button_down_Xopt:	[self._devices['shortrangemover'].move_down_continuous,'Xopt'],
			self.button_up_Yopt:	[self._devices['shortrangemover'].move_up_continuous,'Yopt'],
			self.button_down_Yopt:	[self._devices['shortrangemover'].move_down_continuous,'Yopt']
		}
		self.shortrangemover_buttongroup = { # links short range movement button with mover move function
			**self.z_buttongroup,
			**self.vgroove_buttongroup
		}
		self.mover_buttongroup = {
			**self.shortrangemover_buttongroup,
			**self.probe_buttongroup
		}
		self.probe_settingsgroup = { # links long range movement settings with mover setter functions
			'frequency': 	[self.probe_frequency, int, ['X','Y']],
			'temperature': 	[self.probe_temp, int, ['X','Y']],
			'step_size': 	[self.probe_power, int, ['X','Y']],
			'steps': 		[self.probe_steps, int, ['X','Y']]
		}
		self.vgroove_settingsgroup = {
			'frequency':	[self.vgroove_frequency, int, ['Xopt','Yopt']],
			'voltage':		[self.vgroove_voltage, int, ['Xopt','Yopt']]
		}
		self.z_settingsgroup = {
			'frequency':	[self.z_frequency, int, ['Z']],
			'voltage':		[self.z_voltage, int, ['Z']]
		}


	def add_validators(self):
		for name, settingsgroup in [['longrangemover',self.probe_settingsgroup],
									['shortrangemover',self.vgroove_settingsgroup],
									['shortrangemover',self.z_settingsgroup]]:
			for key in settingsgroup:
				self._add_validator(name,key,settingsgroup)


	def _add_validator(self,movertype,name,settingsgroup):
		limits = self._devices[movertype].get_limits()
		if limits[name][0] == int:
			validator = QtGui.QIntValidator(limits[name][1],limits[name][2])
			settingsgroup[name][0].setValidator(validator)


	def resizeEvent(self,event):
		self.fig.tight_layout()
		self.canvas.draw_idle()
		event.accept()


	def _set_device_settings(self):
		for button in self.mover_buttongroup:
			if button.isDown() and button in self.probe_buttongroup:
				bundle = self._make_bundle(self.probe_settingsgroup)
				self._devices['longrangemover'].set_settings(bundle)
				break
			elif button.isDown() and button in self.vgroove_buttongroup:
				bundle = self._make_bundle(self.vgroove_settingsgroup)
				self._devices['shortrangemover'].set_settings(bundle)
				break
			elif button.isDown() and button in self.z_buttongroup:
				bundle = self._make_bundle(self.z_settingsgroup)
				self._devices['shortrangemover'].set_settings(bundle)
				break


	def _make_bundle(self,settingsgroup):
		bundle = {}
		for setting, [widget, totype, axes] in settingsgroup.items():
			if type(widget) == QtWidgets.QLineEdit:
				value = totype(widget.text())
				bundle[setting] = [value,axes]
			else:
				raise ValueError
		return bundle


	gotoFinished = QtCore.pyqtSignal(str)

	@QtCore.pyqtSlot(str)
	def _goto_reset(self,stopped_channel):
		self._going_to[stopped_channel] = False
		is_moving = False
		for channel, moving in self._going_to.items():
			if moving:
				is_moving = True
		if not is_moving:
			self.button_goto.setText('Go')
			self.enable_other_tabs(True)


	@QtCore.pyqtSlot()
	def on_goto_clicked(self):
		was_moving = False
		for channel, moving in self._going_to.items():
			if moving:
				was_moving = True
				self._devices['shortrangemover'].stop(channel)
				self._going_to[channel] = False
		if was_moving:
			self.button_goto.setText('Go')
			self.enable_other_tabs(True)
		else:
			target = {}
			try:
				target['Xopt'] = float(self.target_Xopt.text())
			except ValueError:
				pass
			try:
				target['Yopt'] = float(self.target_Yopt.text())
			except ValueError:
				pass

			bundle = self._make_bundle(self.vgroove_settingsgroup)
			self._devices['shortrangemover'].set_settings(bundle)
			for channel, pos in target.items():
				self._devices['shortrangemover'].move_to(channel,pos,signal=self.gotoFinished)
				self._going_to[channel] = True
			if len(target) > 0:
				self.button_goto.setText('Stop')
				self.enable_other_tabs(False)


	@QtCore.pyqtSlot()
	def on_scan_clicked(self):
		manager = self._managers['rastermanager']
		if manager.active:
			self.on_scan_finished()
		else:
			range_ = []
			for widget in (self.from_Xopt, self.to_Xopt, self.from_Yopt, self.to_Yopt):
				try:
					range_.append(float(widget.text()))
				except:
					logger.error('Tried to run scan without setting value for {}'.format(widget))
			manager.set_range(range_)
			bundle = self._make_bundle(self.vgroove_settingsgroup)
			manager.mover.set_settings(bundle)

			try:
				self._thread_pause_flags['powermeter']['pause'] = True
				manager.run()
				self.enable_other_tabs(False)
				self.button_scan.setText('Stop')
			except (AssertionError,ValueError) as e:
				logger.error('Failed to run manager: {}'.format(e))


	@QtCore.pyqtSlot()
	def on_scan_reset_clicked(self):
		response = QtWidgets.QMessageBox.question(self,
			'Reset scan?','Are you sure you want to discard current scan data?',
			QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No,
			QtWidgets.QMessageBox.No)
		if response == QtWidgets.QMessageBox.Yes:
			self._managers['rastermanager'].reset_data()
			self._update_graphs()


	def enable_other_tabs(self,enable):
		idx = self.tabWidget.currentIndex()
		for i in range(self.tabWidget.count()):
			if i != idx:
				self.tabWidget.setTabEnabled(i,enable)


	@QtCore.pyqtSlot()
	def on_hold_clicked(self):
		manager = self._managers['holdmanager']
		if manager.active:
			manager.stop()
			self.enable_other_tabs(True)
			self.button_hold.setText('Hold')
		else:
			bundle = self._make_bundle(self.vgroove_settingsgroup)
			manager.mover.set_settings(bundle)
			try:
				manager.run()
				self.enable_other_tabs(False)
				self.button_hold.setText('Stop')
			except (AssertionError,ValueError) as e:
				logger.error('Failed to run manager: {}'.format(e))


	@QtCore.pyqtSlot()
	def on_longrangemover_pressed(self):
		self._set_device_settings()
		self._longrangemove()
		self._movertimer.start(self._settings.get('SW','longrangemover','repeatrate'))


	@QtCore.pyqtSlot()
	def on_longrangemover_released(self):
		self._movertimer.stop()


	@QtCore.pyqtSlot()
	def _longrangemove(self):
		for button, (func, param) in self.probe_buttongroup.items():
			if button.isDown():
				if self._settings.get('SW','global','triggerbackedoffmessage') == True and button in [self.button_up_X,
					self.button_down_X,self.button_up_Y,self.button_down_Y]:
						response = QtWidgets.QMessageBox.question(self,
							'Warning','Is Z backed off?',
							QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No,
							QtWidgets.QMessageBox.No)
						if response == QtWidgets.QMessageBox.Yes:
							self._settings.set(('SW','global','triggerbackedoffmessage'),False)
				else:
					try:
						func(param)
					except (IndexError,CacliError) as e:
						logger.error('error moving: {}'.format(e))


	@QtCore.pyqtSlot()
	def on_shortrangemover_pressed(self):
		self._set_device_settings()
		for button, (func, param) in self.shortrangemover_buttongroup.items():
			if button.isDown():
				func(param)
				self._currently_moving.append(button)


	@QtCore.pyqtSlot()
	def on_shortrangemover_released(self):
		for button in self._currently_moving:
			if button.isDown() == False:
				self._devices['shortrangemover'].stop(self.shortrangemover_buttongroup[button][1])
				self._currently_moving.pop(self._currently_moving.index(button))


	@QtCore.pyqtSlot(int)
	def on_probe_temp_auto(self,val):
		target_sensor = self._measurementgroup[self._settings.get('SW','global','probeautotempsensor')]#self.T1_value
		if val == 0: #if False (val is 3-state)
			self.probe_temp.setReadOnly(False)
			self.probe_temp.setEnabled(True)
			try:
				self._probe_temp_value_connected_sensor.disconnect()
			except AttributeError:
				pass
		else:
			self.probe_temp.setReadOnly(True)
			self.probe_temp.setEnabled(False)
			target_sensor.textChanged.connect(self._probe_temp_auto_handler)
			self._probe_temp_auto_handler(target_sensor.text())
			self._probe_temp_value_connected_sensor = target_sensor


	@QtCore.pyqtSlot(str)
	def _probe_temp_auto_handler(self,value):
		try:
			value = int(float(value))
			value = value if value >= 1 and value <=300 else 1 if value < 1 else 300
		except ValueError:
			pass
		self.probe_temp.setText(str(value))


	@QtCore.pyqtSlot()
	def on_static_voltage_change(self):
		self._vctimer.start(500)


	@QtCore.pyqtSlot()
	def _update_graphs(self):
		try:
			self._active_diagram.set_attocube_position(float(self.Xopt_value.text()),float(self.Yopt_value.text()))
		except ValueError:
			pass
		try:
			self._active_diagram.set_janssen_position(int(self.X_value.text()),int(self.Y_value.text()))
		except (ValueError,AttributeError):
			pass
		try:
			rasterdata = self._managers['rastermanager'].get_data()
			self._active_diagram.set_scan_data(rasterdata['Xopt'],rasterdata['Yopt'],rasterdata['meas'])
		except ValueError as e:
			logger.info(e)
		except AttributeError: 
			pass
		self.canvas.draw_idle()


	@QtCore.pyqtSlot()
	def _static_voltage_change(self):
		self._devices['shortrangemover'].set_static_amplitude(float(self.global_voltage.cleanText()))


	updateMeasurement = QtCore.pyqtSignal(dict)
	updatePositions = QtCore.pyqtSignal(dict)
	scanFinished = QtCore.pyqtSignal()


	@QtCore.pyqtSlot()
	def on_scan_finished(self):
		self._managers['rastermanager'].stop()
		self.button_scan.setText('Scan')
		self._thread_pause_flags['powermeter']['pause'] = False
		self.enable_other_tabs(True)


	@QtCore.pyqtSlot(dict)
	def on_update_positions(self,positions):
		for key, value in positions.items():
			box = {'X':self.X_value,'Y':self.Y_value,'Z':self.Z_value,'Xopt':self.Xopt_value,'Yopt':self.Yopt_value}[key]
			value = str(round(value,5)) if type(value) == float else str(value)
			box.setText(value)


