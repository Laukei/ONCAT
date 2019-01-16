import json

from PyQt5 import QtGui, QtCore, QtWidgets #QtWebEngineWidgets
from PyQt5.uic import loadUi

class SettingsDialog(QtWidgets.QDialog):
	def __init__(self,settings):
		super().__init__()
		self._settings = settings
		loadUi('oncat/ui/settings.ui',self)

		self.load_settings()
		self.buttonBox.clicked.connect(self.buttonboxclicked)
		self.buttonBox.accepted.connect(self.accepted)
		self.show()


	def load_settings(self,reset=False):
		if reset == False:
			self.settingsTextEdit.setPlainText(self._settings.get_plaintext())
		else:
			self.settingsTextEdit.setPlainText(self._settings.get_defaults())

	def buttonboxclicked(self,button):
		if button == self.buttonBox.button(QtWidgets.QDialogButtonBox.RestoreDefaults):
			self.load_settings()

	def accepted(self):
		try:
			self._settings.set_plaintext(self.settingsTextEdit.toPlainText())
			self._settings.save()
		except json.decoder.JSONDecodeError:
			QtWidgets.QMessageBox.information(self, "Problem parsing changes",
					"Unable to convert changed settings to JSON - changes were not saved.")