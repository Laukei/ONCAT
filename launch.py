import sys

from PyQt5.QtWidgets import QApplication

from oncat.splash import make_splash

def launch():
	app = QApplication(sys.argv)
	splash = make_splash()
	app.processEvents()
	from oncat.gui import MainWindow
	main = MainWindow()
	splash.finish(main)
	sys.exit(app.exec_())




if __name__ == "__main__":
	launch()