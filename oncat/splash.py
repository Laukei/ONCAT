from PyQt5.QtGui import QPixmap 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplashScreen

def make_splash():
	splash_pic = QPixmap('oncat/img/splash.png')
	splash = QSplashScreen(splash_pic, Qt.WindowStaysOnTopHint)
	splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
	splash.setEnabled(True)
	splash.show()
	return splash