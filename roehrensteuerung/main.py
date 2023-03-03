#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from spellman import spellman_uX50P50
# for development purposes at home comment in the following line and uncomment the line before.
#from spellman_debug import spellman_uX50P50
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QInputDialog, QDialog, QTabWidget, QHBoxLayout, QGroupBox, QDoubleSpinBox, QLCDNumber, QLineEdit, QProgressBar, QLabel
from PyQt5.QtCore import pyqtSlot, QTimer, Qt
from PyQt5 import uic, QtGui


class Ui(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        
        #self.generator = spellman_MNX50P50('192.168.1.4', 50001)
        self.generator = spellman_uX50P50('192.168.60.250', 50001)
        
        self.warning = QtGui.QPixmap(os.getcwd() + "/warning.png").scaled(100, 100, Qt.KeepAspectRatio)
        self.safe = QtGui.QPixmap(os.getcwd() + "/safe.png").scaled(100, 100, Qt.KeepAspectRatio)
        self.on = QtGui.QPixmap(os.getcwd() + "/on.png").scaled(20, 20, Qt.KeepAspectRatio)
        self.off = QtGui.QPixmap(os.getcwd() + "/off.png").scaled(20, 20, Qt.KeepAspectRatio)
        
        self.voltage_button = self.findChild(QPushButton, 'voltage_button')
        self.current_button = self.findChild(QPushButton, 'current_button')
        self.preheat_button = self.findChild(QPushButton, 'preheat_button')
        self.filament_button = self.findChild(QPushButton, 'filament_button')
        #self.connect_button = self.findChild(QPushButton, 'connect_button')
        self.hv_on_button = self.findChild(QPushButton, 'hv_on_button')
        self.hv_off_button = self.findChild(QPushButton, 'hv_off_button')
        self.reset_fault_button = self.findChild(QPushButton, 'reset_fault_button')
        
        self.voltage_field = self.findChild(QDoubleSpinBox, 'voltage_field')
        self.current_field = self.findChild(QDoubleSpinBox, 'current_field')
        self.preheat_field = self.findChild(QDoubleSpinBox, 'preheat_field')
        self.filament_field = self.findChild(QDoubleSpinBox, 'filament_field')
        #self.ip_field = self.findChild(QLineEdit, 'ip_field')
        #self.port_field = self.findChild(QLineEdit, 'port_field')
        
        self.voltage_indicator = self.findChild(QLCDNumber, 'voltage_indicator')
        self.current_indicator = self.findChild(QLCDNumber, 'current_indicator')
        self.preheat_indicator = self.findChild(QLCDNumber, 'preheat_indicator')
        self.filament_indicator = self.findChild(QLCDNumber, 'filament_indicator')
        
        
        self.filament_limit_setpoint_indicator = self.findChild(QLCDNumber, 'filament_limit_setpoint_indicator')
        self.voltage_setpoint_indicator = self.findChild(QLCDNumber, 'voltage_setpoint_indicator')
        self.current_setpoint_indicator = self.findChild(QLCDNumber, 'current_setpoint_indicator')
        
        
        
        self.filament_voltage_indicator = self.findChild(QLCDNumber, 'filament_voltage_indicator')
        
        self.hv_alt_indicator = self.findChild(QLCDNumber, 'hv_alt_indicator')
        self.lv_indicator = self.findChild(QLCDNumber, 'lv_indicator')
        
        self.lv_temp = self.findChild(QProgressBar, 'lv_temp')
        self.hv_temp = self.findChild(QProgressBar, 'hv_temp')
        
        self.hv_on_label = self.findChild(QLabel, 'hv_on_label')
        self.hv_on_warning = self.findChild(QLabel, 'hv_on_warning')
        
        self.interlock_open_label = self.findChild(QLabel, 'interlock_open_label')
        self.interlock_fault_label = self.findChild(QLabel, 'interlock_fault_label')
        self.overvoltage_label = self.findChild(QLabel, 'overvoltage_label')
        self.config_fault_label = self.findChild(QLabel, 'config_fault_label')
        self.overpower_label = self.findChild(QLabel, 'overpower_label')
        self.undervoltage_label = self.findChild(QLabel, 'undervoltage_label')
        
        self.voltage_button.clicked.connect(self.set_hv)
        self.current_button.clicked.connect(self.set_current)
        self.preheat_button.clicked.connect(self.set_preheat)
        self.filament_button.clicked.connect(self.set_filament)
        
        self.hv_on_button.clicked.connect(self.hv_on)
        self.hv_off_button.clicked.connect(self.hv_off)
        self.reset_fault_button.clicked.connect(self.reset)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(200)
        
        self.show()
        
    
    @pyqtSlot()
    def update(self):
        
        self.lv_temp.setValue(self.generator.lv_board_temp)
        self.lv_indicator.display(self.generator.lv_supply_voltage) # in Volt
        self.voltage_indicator.display(self.generator.voltage/1000) # /1000, da Anzeige in kV
        self.current_indicator.display(self.generator.current) # in uA. Label in ui Datei ändern!
        self.filament_indicator.display(self.generator.fil_current) # in mA
        self.filament_voltage_indicator.display(self.generator.fil_voltage) # in Volt
        self.hv_temp.setValue(self.generator.hv_board_temp)
        
        if self.generator.hv_on == True:
            self.hv_on_label.setText('HV On')
            self.hv_on_warning.setPixmap(self.warning)
        else:
            self.hv_on_label.setText('HV Off')
            self.hv_on_warning.setPixmap(self.safe)
            
            
        if self.generator.interlock_open == True:
            self.interlock_open_label.setPixmap(self.on)
        else:
            self.interlock_open_label.setPixmap(self.off)
        
        
        if self.generator.interlock_fault == True:
            self.interlock_fault_label.setPixmap(self.on)
        else:
            self.interlock_fault_label.setPixmap(self.off)
        
        
        if self.generator.overvoltage_fault == True:
            self.overvoltage_label.setPixmap(self.on)
        else:
            self.overvoltage_label.setPixmap(self.off)
        
        
        if self.generator.configuration_fault == True:
            self.config_fault_label.setPixmap(self.on)
        else:
            self.config_fault_label.setPixmap(self.off)
        
        
        if self.generator.overpower_fault == True:
            self.overpower_label.setPixmap(self.on)
        else:
            self.overpower_label.setPixmap(self.off)
            
        
        if self.generator.lv_undervoltage_fault == True:
            self.undervoltage_label.setPixmap(self.on)
        else:
            self.undervoltage_label.setPixmap(self.off)
        
        
        self.voltage_setpoint_indicator.display(self.generator.voltage_setpoint/1000) # /1000, da Anzeige in kV
        
        self.hv_alt_indicator.display(self.generator.aux_voltage/1000) # /1000, da Anzeige in kV
        
        self.current_setpoint_indicator.display(self.generator.current_setpoint) # in µA
        
        self.preheat_indicator.display(self.generator.fil_current_setpoint) # in mA
        
        self.filament_limit_setpoint_indicator.display(self.generator.fil_maxcurrent) # in mA
            
    @pyqtSlot()
    def set_hv(self):
        self.generator.set_voltage(1000*self.voltage_field.value()) # mal 1000, da Anzeige in kV, aber Funktion Spannung in V erwartet
        
    @pyqtSlot()
    def set_current(self):
        self.generator.set_current(self.current_field.value()) # in uA. Label in ui Datei ändern!
        
    @pyqtSlot()
    def set_preheat(self):
        self.generator.set_fil_preheat(self.preheat_field.value()) # in mA
    
    @pyqtSlot()
    def set_filament(self):
        self.generator.set_fil_maxcurrent(self.filament_field.value()) # in mA
        
    @pyqtSlot()
    def hv_on(self):
        self.generator.enable_hv()
        
    @pyqtSlot()
    def hv_off(self):
        self.generator.disable_hv()

    @pyqtSlot()
    def reset(self):
        self.generator.reset_faults()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Ui()
    app.exec_()
