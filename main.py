import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import QTimer
from configparser import ConfigParser
from PlcModTCP import get_dmc_number
from errorLogger import LogError
import socket

class Mainwindow(QMainWindow):
    def __init__(self):
        super(Mainwindow, self).__init__()
        self.setWindowTitle("Video Capture Station")
        loadUi("main.ui", self)
        #self.logger = LogError.GetLogger()
        self.logger = LogError.get_logger()

        self.red_on = True
        #self.green_on = False
       
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.toggle_leds)
        # self.timer.start(1000)  # 1000 ms = 1 sec

        self.BtnStart.clicked.connect(self.start_action)
        self.BtnStop.clicked.connect(self.stop_action)
        self.BtnConfig.clicked.connect(self.config_action)

        config = ConfigParser()

        config.read('config.ini')
        self.logger.info('Application Version:'+str(config.get('Application','VERSION')))
        self.PLCIp = str(config.get('Application','PLCIP'))
        print(self.PLCIp)
                

    def start_action(self):
        self.update_led('green')

    def stop_action(self):
        print("Stop clicked")

    def config_action(self):
      self.config_window = ConfigWindow()   # create dialog
      self.config_window.show()  

    def toggle_leds(self):
        """Swap red/green LED states"""
        self.red_on = not self.red_on
        #self.green_on = not self.green_on
        self.update_leds()

    def update_leds(self):
        """Update LED colors based on states"""
        self.ledRed.setStyleSheet(
            "background-color: red; border-radius: 12px;" if self.red_on
            else "background-color: grey; border-radius: 12px;"
        )
        # self.ledGreen.setStyleSheet(
        #     "background-color: green; border-radius: 12px;" if self.green_on
        #     else "background-color: grey; border-radius: 12px;"
        # )

    def update_led(self, color_name):
        """Set LED color dynamically"""
        self.led.setStyleSheet(
        f"background-color: {color_name}; border-radius: 28px;"
        )

    def cycle_start(self):
        self.update_led('green')
        dmc = get_dmc_number(self.config.get('Application','plcip'),self.config.get('Application','plc_port'),666) 


class ConfigWindow(QMainWindow):   # config dialog
    def __init__(self):
        print('Open Config Window')
        super(ConfigWindow, self).__init__()
        loadUi("configuration.ui", self)

        self.config = ConfigParser()
        self.config.read('config.ini')
        
        self.btnSave.clicked.connect(self.btnSave_clicked)
        self.btnBack.clicked.connect(self.btnBack_clicked)
        self.btnTestConnection.clicked.connect(self.btnTestConnection_clicked)

        ##PLC IP
        PLCIp = str(self.config.get('Application','PLCIP'))
        self.txtIP.setText(PLCIp)

        ##PLC Port
        plc_port = str(self.config.get('Application','plc_port'))
        self.txtPort.setText(plc_port)

        ##USN TAG
        usn_tag = str(self.config.get('Application','usn_tag'))
        self.txtUSNTag.setText(usn_tag)


        ##ack Tag
        ack_tag = str(self.config.get('Application','ack_tag'))
        self.txtAckTag.setText(ack_tag)


        ##Cycle Start
        cycle_start_stop = str(self.config.get('Application','cycle_start_stop'))
        self.txtCycleStart.setText(cycle_start_stop)


        #self.comboPLC.currentIndexChanged.connect(self.selection_changed)
        if "Stations" in self.config:
            for station_id, station_name in self.config["Stations"].items():
                # Add text + hidden ID
                self.comboPLC.addItem(station_name, station_id)

        saved_id = self.config.getint("Application", "plc_id", fallback=-1)

        # find index of item with this ID
        idx = self.comboPLC.findData(saved_id)
        if idx >= 0:
            self.comboPLC.setCurrentIndex(idx)
  

    def selection_changed(self, index):
        text = self.comboPLC.currentText()
        station_id = self.comboPLC.itemData(index)
        print(f"Selected: {text} (ID={station_id})")
    
    def btnSave_clicked(self):
        print('Save Button Clicked')
        self.config.set("Application", "PLCIP", self.txtIP.text())
        self.config.set("Application", "plc_port", self.txtPort.text())
        self.config.set("Application", "usn_tag", self.txtUSNTag.text())
        self.config.set("Application", "ack_tag", self.txtAckTag.text())

        selected_id = self.comboPLC.currentData()   
        self.config.set("Application", "plc_id", selected_id)
        self.config.set("Application", "cycle_start_stop", self.txtCycleStart.text())

        
        with open("config.ini", "w") as f:
            self.config.write(f)
            
        QMessageBox.information(self, "Success", "Settings saved successfully!")


    def btnBack_clicked(self):
        self.close()
    def btnTestConnection_clicked(self):

        HOST = self.config.get('Application','PLCIP')
        PORT = int(self.config.get('Application','plc_port'))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 sec timeout

        try:
            sock.connect((HOST, PORT))
            #QMessageBox.information(self, "Success", "Connection is successful")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Connection Status")
            msg.setText(f"Connected successfully to {HOST}:{PORT}")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        except socket.timeout:
            #QMessageBox.critical(self, "Failure", "Connection is successful")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Connection Status")
            msg.setText(f"Failed to connect to {HOST}:{PORT}")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

        except socket.error as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Connection Status")
            msg.setText(f"❌ Failed to connect to {HOST}:{PORT}")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        finally:
            sock.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = Mainwindow()
    mainwindow.setWindowTitle("Video Capture")
    mainwindow.show()
    app.exec()