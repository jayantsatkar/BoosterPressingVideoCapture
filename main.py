import os
import string
import sys
import threading
import time
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import QTimer
from configparser import ConfigParser
#from PlcModTCP import PLCClient_original #, get_dmc_number
from plcclient import PLCClient #, get_dmc_number
from errorLogger import LogError
import socket
import numpy as np
import mss

from screen_recorder import ScreenRecorder
class Mainwindow(QMainWindow):
    def __init__(self):
        super(Mainwindow, self).__init__()
        self.setWindowTitle("Video Capture Station")
        loadUi("main.ui", self)
        #self.logger = LogError.GetLogger()
        self.logger = LogError.get_logger()

        self.red_on = True

        self.BtnStart.clicked.connect(self.start_action)
        self.BtnStop.clicked.connect(self.stop_action)
        self.BtnConfig.clicked.connect(self.config_action)
        self.lblUSNText.setText('')

        self.config = ConfigParser()
        self._stop_event = threading.Event()

        self.config.read('config.ini')
        self.logger.info('Application Version:'+str(self.config.get('Application','VERSION')))
        self.PLCIp = str(self.config.get('Application','PLCIP'))
        self.logger.info('PLC IP:'+str(self.config.get('Application','PLCIP')))     
        self.addr_cycle_start_stop = int(self.config.get('Application', 'cycle_start_stop'))     
        self.addr_heartbeat = int(self.config.get('Application', 'heartbeat_tag')) 

        plc = PLCClient(self.config.get('Application','plcip'),int(self.config.get('Application','plc_port')),self.logger)
        self.plc = plc

        threading.Thread(target=self._send_heartbeat, daemon=True).start()     
        threading.Thread(target=self._monitor_cycle, daemon=True).start()

    def _send_heartbeat(self):
        """Toggle heartbeat bit periodically"""
        toggle = False
        while not self._stop_event.is_set():
            try:
                self.plc.write_bool(self.addr_heartbeat, toggle)
                toggle = not toggle
                time.sleep(0.5)
            except Exception as ex:
                if self.logger:
                    self.logger.error(f"Heartbeat error: {ex}")
                else:
                    print("Heartbeat error:", ex)
                time.sleep(2)

    def _monitor_cycle(self):
        """Monitor single tag for cycle start/stop and read DMC"""
        last_cycle_state = False  # previous value

        while not self._stop_event.is_set():
            try:
                cycle_state = self.plc.read_bool( address = self.addr_cycle_start_stop)  # same tag for start/stop

                # Rising edge → cycle started
                if cycle_state and not last_cycle_state:
                    dmc = self.plc.read_dmc_number(int(self.config.get('Application','usn_tag')), count=10)
                    if dmc != None:
                        dmc_clean = ''.join(c for c in dmc if c in string.printable and not c.isspace())
                        self.logger.info('DMC Number Logged='+ str(dmc_clean))
                    if self.logger:
                        self.logger.info(f"Cycle Started. DMC: {dmc_clean}")
                    else:
                        print(f"Cycle Started. DMC: {dmc_clean}")

                # Falling edge → cycle stopped
                if not cycle_state and last_cycle_state:
                    if self.logger:
                        self.logger.info("Cycle Stopped")
                    else:
                        print("Cycle Stopped")

                # Remember last state for edge detection
                last_cycle_state = cycle_state

                time.sleep(0.5)
            except Exception as ex:
                if self.logger:
                    self.logger.error(f"Cycle monitor error: {ex}")
                else:
                    print("Cycle monitor error:", ex)
                time.sleep(2)

    def start_action(self):
        self.update_led('green')
        self.cycle_start()

    def stop_action(self):
        print("Stop clicked")
        self.cycle_stop()

    def config_action(self):
      enable_config = self.config.getboolean("Application", "enable_config", fallback=False)
      
      if enable_config == True:
        self.config_window = ConfigWindow()   # create dialog
        self.config_window.show() 
      else:
            QMessageBox.warning(self, "Warning", "Access denied!")


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
        self.led.setStyleSheet(f"background-color: {color_name}; border-radius: 28px;")

    def cycle_start(self):
        try:
            self.update_led('green')
            self.logger.info('Cycle Started')
            #dmc = get_dmc_number(self.config.get('Application','plcip'),self.config.get('Application','plc_port'),10) 

            #plc = PLCClient(self.config.get('Application','plcip'),int(self.config.get('Application','plc_port')),self.logger)
            #self.plc = plc
            dmc = self.plc.read_dmc_number(int(self.config.get('Application','usn_tag')), count=10)
            #dmc = ""

            if dmc != None:
                #newdmc = ''.join(chr(r) for r in dmc if 32 <= r <= 126)
                dmc_clean = ''.join(c for c in dmc if c in string.printable and not c.isspace())

                self.logger.info('DMC Number Logged='+ str(dmc_clean))
                
                self.lblMessage.setText(f'Video recording started')
                self.lblUSNText.setText(dmc_clean)
                self.is_capture_started = True
                self.dmc = dmc_clean
                self.start_capture(dmc_clean)
                
                
            else:
                self.update_led('red')
                
                self.lblMessage.setText('Error while processing. Please check logs')
        except Exception as E:
            self.logger.fatal(E)
            self.update_led('red')
    
    def start_capture(self, dmc_clean):
        self.recorder = ScreenRecorder(dmc_clean)
        self.recorder.start()

    def cycle_stop(self):
        try:
            self.update_led('orange')
            self.logger.info('Cycle Stopped')
            #self.is_capture_started = False
            self.recorder.stop()
                
            self.lblMessage.setText('Video saved successfully')
        except Exception as E:
            self.logger.fatal(E)
            self.update_led('red')



class ConfigWindow(QMainWindow):   # config dialog
    def __init__(self):
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