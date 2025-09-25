import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi
from PyQt6.QtCore import QTimer


class Screencap(QMainWindow):
    def __init__(self):
        super(Screencap, self).__init__()
        self.setWindowTitle("Video Capture Station")
        loadUi("screencapturemain.ui", self)

        ##Fix the Screen Size
        #self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        # Also prevent resizing if needed
        # Remove maximize button but keep close and minimize buttons
        #self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)

        # Optional: Fix the window size to current size (prevents resizing)
        #self.setFixedSize(self.size())

        self.red_on = True
        self.green_on = False
       
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_leds)
        self.timer.start(1000)  # 1000 ms = 1 sec

        self.BtnStart.clicked.connect(self.start_action)
        self.BtnStop.clicked.connect(self.stop_action)
        self.BtnConfig.clicked.connect(self.config_action)


    def start_action(self):
        print("Start clicked")

    def stop_action(self):
        print("Stop clicked")

    def config_action(self):
      self.config_window = ConfigDialog()   # create dialog
      self.config_window.show()  

    def toggle_leds(self):
        """Swap red/green LED states"""
        self.red_on = not self.red_on
        self.green_on = not self.green_on
        self.update_leds()

    def update_leds(self):
        """Update LED colors based on states"""
        self.ledRed.setStyleSheet(
            "background-color: red; border-radius: 12px;" if self.red_on
            else "background-color: grey; border-radius: 12px;"
        )
        self.ledGreen.setStyleSheet(
            "background-color: green; border-radius: 12px;" if self.green_on
            else "background-color: grey; border-radius: 12px;"
        )

class ConfigDialog(QMainWindow):   # config dialog
    def __init__(self):
        print('QMainWindow')
        super(ConfigDialog, self).__init__()
        loadUi("screenrecordstation.ui", self)

app = QApplication(sys.argv)
mainwindow = Screencap()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)      
widget.setGeometry(100, 100, 600, 400)  # x, y, width, height

widget.show()
app.exec()