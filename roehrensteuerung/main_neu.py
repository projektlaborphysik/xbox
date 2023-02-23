#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import path
import time
import numpy as np

#from spellman import spellman_uX50P50
from spellman_debug import spellman_uX50P50
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QInputDialog, QDialog, QTabWidget, QHBoxLayout, QGroupBox, QDoubleSpinBox, QLCDNumber, QLineEdit, QProgressBar, QLabel, QPlainTextEdit
from PyQt5.QtCore import pyqtSlot, QTimer, Qt
from PyQt5 import uic, QtGui


# Daten zum Einfahren
voltage_list = [  5,  10,  15,  20,  25,  35,   45,   50,  50 ]
#time_list     = [ 30,  30,  30,  30,  30, 600,  600,  600]
# test time list
time_list     = [ 10,  10,  10,  20,  20, 30,  30,  30]

#%%

# Maximalwerte (Maximaler Strom unterhalb der angegebenen Spannungswerte)
voltage_max_list = np.array([-1,  0,   5,  10,  15,  20,  25,  30,  35,   40,   45,   50, 50.001])
current_max_list = np.array([ 0,  0, 100, 200, 350, 450, 600, 830, 900, 1000, 1000, 1000, 1000])
max_current_value = 1000
max_voltage_value = 50

def max_current(voltage):
    index = np.where(voltage_max_list > voltage)[0][0]
    return(current_max_list[index-1])

def min_voltage(current):
    index = np.where(current_max_list >= current)[0][0]
    return(voltage_max_list[index])

#%%
    


class Ui(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        
        # In diesem Ordern werden alle log-Dateien abgelegt.
        # Bitte entsrechend anpassen!
        self.LOG_FOLDER = r'C:\Users\mail\Desktop\logging_folder'
        
        #self.generator = spellman_MNX50P50('192.168.1.4', 50001)
        self.generator = spellman_uX50P50('127.0.0.1', 50001)
        
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
        
        self.notification_field = self.findChild(QPlainTextEdit, 'notifications')
        
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
        
        self.voltage_setpoint_indicator.display(self.generator.voltage_setpoint)
        self.current_setpoint_indicator.display(self.generator.current_setpoint)
        
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
        if self.voltage_field.value() <= max_voltage_value:
            if self.generator.current_setpoint <= max_current(self.voltage_field.value()):
                self.generator.set_voltage(1000*self.voltage_field.value()) # mal 1000, da Anzeige in kV, aber Funktion Spannung in V erwartet
                time.sleep(1.1)
                self.log_status('(voltage setpoint changed)')
            else:
                self.log_status('(voltage setpoint is to low for current)')
        else:
            self.log_status('(current setpoint exceeds maximum voltage of 50 kV)')
    
    @pyqtSlot()
    def set_current(self):
        if self.current_field.value() <= max_current_value:
            if self.generator.voltage_setpoint >= min_voltage(self.current_field.value())*1000:
                self.generator.set_current(self.current_field.value()) # in uA. Label in ui Datei ändern!
                time.sleep(1.1)
                self.log_status('(current setpoint changed)')
            else:
                self.log_status('(current setpoint is to high for voltage)')
        else:
            self.log_status('(current setpoint exceeds maximum current of 1000 uA)')
    
    @pyqtSlot()
    def set_preheat(self):
        self.generator.set_fil_preheat(self.preheat_field.value()) # in mA
    
    @pyqtSlot()
    def set_filament(self):
        self.generator.set_fil_maxcurrent(self.filament_field.value()) # in mA
        
    @pyqtSlot()
    def hv_on(self):
        if self.last_tube_usage() == 'unbekannt':
            self.notification_field.appendPlainText('Die letzte Nutzung der Röntgenquelle ist nicht bekannt!\n'
                                                    +'Bitte Röhre nach Bedienungsanleitung hochfahren!')
            dlg = CustomDialog(self)
            dlg.exec()
            time.sleep(1.1)
            self.log_status('(no voltage)')
        else:
            last_time = self.last_tube_usage()
            last_time_s = time.mktime(time.strptime(last_time, '%Y-%m-%d-%H:%M:%S'))
            actual_time = time.mktime(time.localtime())
            time_weeks = (actual_time-last_time_s)/(3600*24*8)
            self.notification_field.appendPlainText('Letzte Nutzung der Röntgenquelle vor '+str(round(time_weeks,1))+' Wochen: '+last_time)
  
            if time_weeks >= 8:
                self.notification_field.appendPlainText('Die letzte Nutzung der Röntgenquelle ist mehr als 8 Wochen her!\n'
                                                        +'Bitte Röhre nach Bedienungsanleitung hochfahren!')
                dlg = CustomDialog(self)
                dlg.exec()
                time.sleep(1.1)
                self.log_status('(no voltage)')
            else:
                self.generator.enable_hv()
                self.notification_field.appendPlainText('Ist die Kühlung in Betrieb?')
                time.sleep(1.1)
                self.log_status('(voltage on)')
        
    @pyqtSlot()
    def hv_off(self):
        self.generator.disable_hv()
        time.sleep(1.1)
        self.log_status('(voltage off)')

    @pyqtSlot()
    def reset(self):
        self.generator.reset_faults()
        
    # Funktionen zum loggen der Röhrensteuerung
    def tube_log(self,text):
        # Pruefen, ob Ordner fuer die log-Dateien existiert
        if not os.path.isdir(self.LOG_FOLDER):
            print('Der Ordner zum speichern der log-Dateien existiert nicht!\n'+
                  'Bitte erzeugen Sie den Ordner\n'+ 
                  self.LOG_FOLDER + 
                  '\noder ändern Sie den Pfad in XXX.py!')
            self.notification_field.appendPlainText('Der Ordner zum speichern der log-Dateien existiert nicht!\n'+
                  'Bitte erzeugen Sie den Ordner\n'+ 
                  self.LOG_FOLDER + 
                  '\noder ändern Sie den Pfad!')
        else:
            # Name des aktuellen Tageslogs erzeugen
            log_name = time.strftime('%Y-%m-%d')+'-xbox-tube.log'

            # Erstellen einer Neuen log-Datei, falls diese fuer den aktuellen Tag
            # noch nicht existiert. 
            if not log_name in os.listdir(self.LOG_FOLDER):
                with open(os.path.join(self.LOG_FOLDER,log_name), 'w') as fp: 
                    pass
                print('Eine neue log-Datei wurde erzeugt.')
                self.notification_field.appendPlainText('Eine neue log-Datei wurde erzeugt.')

            # Anhaengen des Eintraages mit Zeitstempel
            with open(os.path.join(self.LOG_FOLDER,log_name), "a") as fp:
                fp.write('[ '+time.strftime('%Y-%m-%d-%H:%M:%S')+' ] '+text+'\n')
            self.notification_field.appendPlainText('[ '+time.strftime('%Y-%m-%d-%H:%M:%S')+' ] '+text)
        return True

    def last_tube_usage(self):
        # Zeitpunkt des letzten Eintrages in den log-Datein mit diesem
        # Schluesselwort wird gesucht.
        key_word = ' U: 45.0 kV, I: 0.0 µA, HV ON'
        
        # Pruefen, ob Ordner fuer die log-Dateien existiert
        if not os.path.isdir(self.LOG_FOLDER):
            print('Der angegebene Ordner mit den log-Dateien existiert nicht!')
            self.notification_field.appendPlainText('Der angegebene Ordner mit den log-Dateien existiert nicht!')
            #return 'unbekannt'

        # Pruefen, ob Dateien im log-Ordner sind
        if os.listdir(self.LOG_FOLDER) == []:
            print('Im angegebenen Ordner existieren keine log-Dateien!')
            self.notification_field.appendPlainText('Im angegebenen Ordner existieren keine log-Dateien!')
            #return 'unbekannt'

        # Sammeln der Dateinamen der log-Dateien
        log_file_list = os.listdir(self.LOG_FOLDER)
        # Sortieren, so dass in neuesten Log-Dateien als erstes gesucht wird
        log_file_list.sort(reverse=True)

        # Die einzelnen log-Dateien werden durchgegangen, beginnend mit der neuesten.
        for file_name in log_file_list:
            # Diese Liste enhält später für diese Datei alle Zeilen,
            # in denen das Schluesselwort gefunden wurde.
            entry_list = []
            
            with open(os.path.join(self.LOG_FOLDER,file_name), 'r') as fp:
                line = fp.readline()
                # Die Zeilen werden solange einzeln gelesen, bis die Datei zu Ende ist.
                while line:
                    # Wird das Schlesselwort gefunden, wird die Zeile der Liste angehängt.
                    if line.find(key_word) != -1:
                        entry_list.append(line)
                    line = fp.readline()
            # Die Liste wird sortiert, sodass der neuste Eintrag an erster Stelle ist.
            entry_list.sort(reverse=True)
            # Hat sie Liste mindestens einen Eintrag, wird der erste Eintrag nach dem
            # Datum geparst, welches als String zurückgegeben wird.
            if len(entry_list) >= 1:
                return entry_list[0][2:21]
        # Falls kein passender Eintrag auffindbar ist, wird 'unbekannt' zurückgegeben.
        return 'unbekannt'
    
    
    def log_status(self,comment = ''):
        if self.generator.hv_on == True:
            hv_string = 'ON'
        else:
            hv_string = 'OFF'
        self.tube_log('U: '+str(self.generator.voltage_setpoint/1000)+' kV, I: '+str(self.generator.current_setpoint)+' µA, HV '+hv_string+' '+comment)

class CustomDialog(QDialog):
    def __init__(self,parent):
        super().__init__()
        uic.loadUi('einfahren.ui', self)
        
        self.parent = parent
        
        self.start_button = self.findChild(QPushButton, 'startButton')
        self.stop_button = self.findChild(QPushButton, 'stopButton')
        self.cancel_button = self.findChild(QPushButton, 'cancelButton')
        self.back_button = self.findChild(QPushButton, 'backButton')
        self.time_display = self.findChild(QLCDNumber, 'timeDisplay')
        self.voltage_display = self.findChild(QLCDNumber, 'voltageDisplay')
        
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)
        self.cancel_button.clicked.connect(self.cancel)
        self.back_button.clicked.connect(self.back)
        self.stop_button.setEnabled(False)
        self.back_button.setEnabled(False)
        
        
        self.step = 0
        self.time_next_step = 0
        self.running = False
        self.time_for_the_next_step = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.parent.update)
        self.timer.timeout.connect(self.drive_source)
        self.timer.start(200)
        
    @pyqtSlot()
    def start(self):
        self.running = True
        self.step = 0
        self.stop_button.setEnabled(True)
        self.back_button.setEnabled(True)
        self.start_button.setEnabled(False)
        self.parent.generator.enable_hv()
        self.parent.generator.set_voltage(voltage_list[self.step]*1000)
        self.parent.generator.set_current(0)
        self.time_for_the_next_step = time.time()+time_list[self.step]
        time.sleep(1.1)
        self.parent.log_status('(automatisches Einfahren)')
        print('start')
        
    
    @pyqtSlot()
    def stop(self):
        if self.running:
            self.running = False
            self.stop_button.setText('Fortsetzen')
            self.pause_time = self.time_for_the_next_step-time.time()
        else:
            self.running = True
            self.stop_button.setText('Pause')
            self.time_for_the_next_step = time.time()+self.pause_time
        print('stop')
       
    @pyqtSlot()
    def cancel(self):
        print('cancel')
        self.running = False
        self.close()
    
    @pyqtSlot()
    def back(self):
        print('back')
        self.step -= 1
        self.parent.generator.set_voltage(voltage_list[self.step]*1000)
        self.time_for_the_next_step = time.time()+time_list[self.step]
        time.sleep(1.1)
        self.parent.log_status('(automatisches Einfahren)')

        
    @pyqtSlot()
    def drive_source(self):
        # start settings
        if self.running:
            self.time_display.display(int(self.time_for_the_next_step-time.time()))
            self.voltage_display.display(voltage_list[self.step+1])
        else:
            self.time_display.display(0)
            self.voltage_display.display(0)
                                        
        if self.running and time.time()>self.time_for_the_next_step:
            if not self.step == 7:
                self.step += 1
                self.parent.generator.set_voltage(voltage_list[self.step]*1000)
                time.sleep(1.1)
                self.parent.log_status('(automatisches Einfahren)')
                self.parent.generator.set_current(0)
                self.time_for_the_next_step = time.time()+time_list[self.step]
            else:
                self.parent.notification_field.appendPlainText('Die Quelle ist eingefahren. Nun kann nach dem normalen Schema den Anodenstrom erhöht werden.')
                self.close()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Ui()
    app.exec_()
