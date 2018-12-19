import sys

from PyQt5 import QtGui, QtCore, QtWidgets #QtWebEngineWidgets
from PyQt5.uic import loadUi
from oncat.settings import Settings


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		name_of_application = "ONCAT Optoelectronic Nanopositioner Control & Alignment Toolkit"
		self.setWindowTitle(name_of_application)
		loadUi('oncat/mainwindow.ui',self)
		self._settings = Settings()
		self.show()
