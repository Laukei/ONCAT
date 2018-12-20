import sys

from PyQt5 import QtGui, QtCore, QtWidgets #QtWebEngineWidgets
from PyQt5.uic import loadUi
from .settings import Settings


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.name_of_application = "ONCAT Optoelectronic Nanopositioner Control & Alignment Toolkit"
		self.setWindowTitle(self.name_of_application)
		loadUi('oncat/mainwindow.ui',self)
		self._settings = Settings()
		self.show()
