import sys

from PyQt5 import QtGui, QtCore, QtWidgets #QtWebEngineWidgets
from PyQt5.uic import loadUi

#from oncat.settings import getSettings


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		name_of_application = "ONCAT Optoelectronic Nanopositioner Control & Alignment Toolkit"
		self.setWindowTitle(name_of_application)
		loadUi('mainwindow.ui',self)
		self.show()



def launch():
	app = QtWidgets.QApplication(sys.argv)
	main = MainWindow()
	sys.exit(app.exec_())

if __name__ == "__main__":
	launch()