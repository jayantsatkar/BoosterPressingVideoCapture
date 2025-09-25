import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QDialog, QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi


class ScreenRecordStation(QDialog):   # second form
    def __init__(self):
        super().__init__()
        print('QDialog')
        loadUi("screenrecordstation.ui", self)

class Screencap(QMainWindow):
    def __init__(self):
        super(Screencap, self).__init__()
        loadUi("screencapturemain.ui", self)

        self.radioBtnoption1.setStyleSheet("""
        QRadioButton::indicator:checked { background-color: green; border: 1px solid black; }
        QRadioButton::indicator:unchecked { background-color: red; border: 1px solid black; }
        """)
        self.radioBtnoption2.setStyleSheet("""
        QRadioButton::indicator:checked { background-color: green; border: 1px solid black; }
        QRadioButton::indicator:unchecked { background-color: red; border: 1px solid black; }
        """)

        # Example of connecting to check change
        self.radioBtnoption1.toggled.connect(self.radio_changed)
        self.radioBtnoption2.toggled.connect(self.radio_changed)

        # connect radio buttons
        self.radioBtnoption1.toggled.connect(self.radio_changed)
        self.radioBtnoption2.toggled.connect(self.radio_changed)

        # connect start/stop buttons
        self.BtnStart.clicked.connect(self.start_action)
        self.BtnStop.clicked.connect(self.stop_action)
        self.BtnConfig.clicked.connect(self.config_action)

    def radio_changed(self):
        if self.radioBtnoption1.isChecked():
            print("Radio Option 1 selected")
        elif self.radioBtnoption2.isChecked():
            print("Radio Option 2 selected")

    def start_action(self):
        print("Start clicked")

    def stop_action(self):
        print("Stop clicked")

    def config_action(self):
      self.config_window = ConfigDialog()   # create dialog
      self.config_window.show()  

        # print("Configure clicked")
    def open_config(self):
        self.config_window = ScreenRecordStation()
        self.config_window.exec()


class ConfigDialog(QMainWindow):   # config dialog
    def __init__(self):
        print('QMainWindow')
        super(ConfigDialog, self).__init__()
        loadUi("screenrecordstation.ui", self)

    
    
app = QApplication(sys.argv)
mainwindow = Screencap()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)      
widget.showMaximized()
widget.setGeometry(100, 100, 700, 600)  # x, y, width, height
widget.show()
app.exec()