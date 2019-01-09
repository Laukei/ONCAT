import sys

from PyQt5 import QtGui, QtCore, QtWidgets #QtWebEngineWidgets
from PyQt5.uic import loadUi

from .settings import Settings
from .monitor import launch_monitor_as_thread, MoverPositionMonitor, BaseMonitor
from .movement import movement_lookup


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.name_of_application = "ONCAT Optoelectronic Nanopositioner Control & Alignment Toolkit"
		self.setWindowTitle(self.name_of_application)
		loadUi('oncat/mainwindow.ui',self)
		self._settings = Settings()
		self._monitors = {}
		self._threads = {}
		self.connect_interface()

		self.start_monitor('longrangemover')
		self.start_monitor('shortrangemover')
		self.show()


	def connect_interface(self):
		self.updatePositions.connect(self.on_update_positions)


	updatePositions = QtCore.pyqtSignal(dict)

	@QtCore.pyqtSlot(dict)
	def on_update_positions(self,positions):
		for key, value in positions.items():
			box = {'X':self.X_value,'Y':self.Y_value,'Z':self.Z_value,'Xopt':self.Xopt_value,'Yopt':self.Yopt_value}[key]
			value = str(round(value,5)) if type(value) == float else str(value)
			box.setText(value)


	def start_monitor(self,identifier):
		if identifier == 'longrangemover':
			self._spin_mover('longrangemover')
		elif identifier == 'shortrangemover':
			self._spin_mover('shortrangemover')


	def _spin_mover(self,identifier):
		selected_class = self._settings.get('SW',identifier)
		self._monitors[identifier] = movement_lookup(selected_class)(**self._settings.get('HW',selected_class))
		self._threads[identifier] = launch_monitor_as_thread(self._monitors[identifier],
															 self._settings.get('HW',selected_class,'lookup'),
															 monitor=MoverPositionMonitor,
															 signal=self.updatePositions,
															 sleeptime=1)
