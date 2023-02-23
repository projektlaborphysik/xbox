#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import sys
import socket
from threading import Thread, Event
from queue import Queue
from distutils.util import strtobool

from configparser import ConfigParser

Start = b'\x02'
End = b',\x03'


# This functions are to simualte the Source with a simple config file
PATH_CONFIG_FILE = "config.ini"

def load_config_value(category,name):
    config_object = ConfigParser()
    config_object.read(PATH_CONFIG_FILE)
    return config_object[category][name]

def write_config_value(category,name,value_string):
    config_object = ConfigParser()
    config_object.read(PATH_CONFIG_FILE)
    config_object[category][name] = value_string
    with open(PATH_CONFIG_FILE, 'w') as configfile:
        config_object.write(configfile)
    return None





class RepeatingTimer(Thread):
    def __init__(self, interval_seconds, callback):
        super().__init__()
        self.stop_event = Event()
        self.interval_seconds = interval_seconds
        self.callback = callback

    def run(self):
        while not self.stop_event.wait(self.interval_seconds):
            self.callback()

    def stop(self):
        self.stop_event.set()


class spellman(object):
    
    def __init__(self, HOST, PORT):
        
        # establish ethernet connection
        # self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # try:
        #     self.connection.connect((HOST, PORT))
            
        # except socket.error as exc:
        #     print('Socket error: %s' % exc)
        #     sys.exit()
        
        
        # # initialize sender and receiver and corresponding queues
        # self.sendqueue = Queue()
        # self.receivequeue = Queue()
        
        # self.receiver = Thread(target=self._receive_ethernet)
        # self.receiver.daemon = True
        # self.receiver.start()
        
        # self.sender = Thread(target=self._send_ethernet)
        # self.sender.daemon = True
        # self.sender.start()
        
        # self.parser = Thread(target=self._parse_response)
        # self.parser.daemon = True
        # self.parser.start()
        
        #time.sleep(2)
        # get device info
        #self._get_device_info()
        
        
        # configure periodic updates of all values
        self.readback_updater = RepeatingTimer(1.0, self._update_readbacks)
        self.readback_updater.daemon = True
        self.readback_updater.start()
        
        self.setpoint_updater = RepeatingTimer(1.0, self._update_setpoints)
        self.setpoint_updater.daemon = True
        self.setpoint_updater.start()
        
        
        # Setpoints for DACs
        self.voltage_setpoint = 0.0
        self.current_setpoint = 0.0
        self.fil_current_setpoint = 0.0
        self.fil_maxcurrent = 0.0
        
        # Analog sensor feedback
        self.voltage = 0.0
        self.aux_voltage = 0.0
        self.current = 0.0
        self.fil_current = 0.0
        self.fil_voltage = 0.0
        self.lv_supply_voltage = 0.0
        self.lv_board_temp = 0.0
        self.hv_board_temp = 0.0
        
        # States
        self.fault = False
        self.hv_on = False
        self.interlock_open = False
        self.interlock_fault = False
        self.overvoltage_fault = False
        self.configuration_fault = False
        self.overpower_fault = False
        self.lv_undervoltage_fault = False
        
        self.voltage = 0.0
        
        
    def _stop(self):
        self.readback_updater.join()
        self.setpoint_updater.join()
        #self.receiver.join()
        #self.sender.join()
        #self.parser.join()
        
    #####################
    # Functions for communication via Ethernet
    #####################
    # def _send_ethernet(self):
    #     while True:
    #         commandstring = self.sendqueue.get()
    #         message = ''.join(['\x02', commandstring, '\x03'])
    #         try:
    #             self.connection.sendall(message.encode())
    #             time.sleep(0.005)
    #         except socket.error as exc:
    #             print('Could not send command: %s' % exc)
    #             self._stop()
    #             sys.exit()
                
    # def _receive_ethernet(self):
    #     while True:
    #         # read from interface
    #         responses = []
    #         frame = self.connection.recv(1024)
            
    #         # search for start of response
    #         if Start in frame:
                
    #             # handle possible multiple responses in one frame
    #             responses = frame.split(Start)[1:]
                
    #             for response in responses:
    #                 # check if response is properly terminated
    #                 if End in response:
    #                     tmp, *_ = response.split(End)
    #                     self.receivequeue.put(tmp.decode())
    #                 else:
    #                     pass
                        
    # #####################
    # # Fetch device information
    # #####################                    
    # def _get_device_info(self):
    #     for i in self._device_info_commands.keys():
    #         self.sendqueue.put(self._device_info_commands[i])
    #     return
    
    #####################
    # Functions for continuous updating of values
    #####################          
          
    def _update_readbacks(self):
        config_object = ConfigParser()
        config_object.read(PATH_CONFIG_FILE)

        
        # Analog sensor feedback
        #self.voltage = 0.0
        self.aux_voltage = float(config_object['FEEDBACK']['aux_voltage'])
        self.current = float(config_object['FEEDBACK']['current'])
        self.voltage = float(config_object['FEEDBACK']['voltage'])
        self.fil_current = float(config_object['FEEDBACK']['fil_current'])
        self.fil_voltage = float(config_object['FEEDBACK']['fil_voltage'])
        self.lv_supply_voltage = float(config_object['FEEDBACK']['lv_supply_voltage'])
        self.lv_board_temp = float(config_object['FEEDBACK']['lv_board_temp'])
        self.hv_board_temp = float(config_object['FEEDBACK']['hv_board_temp'])
        
        # States
        self.fault = bool(strtobool(config_object['STATES']['fault']))
        self.hv_on = bool(strtobool(config_object['STATES']['hv_on']))
        self.interlock_open = bool(strtobool(config_object['STATES']['interlock_open']))
        self.interlock_fault = bool(strtobool(config_object['STATES']['interlock_fault']))
        self.overvoltage_fault = bool(strtobool(config_object['STATES']['overvoltage_fault']))
        self.configuration_fault = bool(strtobool(config_object['STATES']['configuration_fault']))
        self.overpower_fault = bool(strtobool(config_object['STATES']['overpower_fault']))
        self.lv_undervoltage_fault = bool(strtobool(config_object['STATES']['lv_undervoltage_fault']))
        
        
    def _update_setpoints(self):
        config_object = ConfigParser()
        config_object.read(PATH_CONFIG_FILE)

        # Setpoints for DACs
        self.voltage_setpoint = float(config_object['SETPOINTS']['voltage'])
        self.current_setpoint = float(config_object['SETPOINTS']['current'])
        self.fil_current_setpoint = float(config_object['SETPOINTS']['fil_current'])
        self.fil_maxcurrent = float(config_object['SETPOINTS']['fil_maxcurrent'])
    
    
    #####################
    # Response parser for Spellman SIC Digital Interface 
    #####################    
    # def _parse_response(self):
    #     while True:
    #         response_string = self.receivequeue.get()
    #         print(response_string)
    #         response_id, *return_values = response_string.split(',')
            
    #         # Parse response for changing anode voltage setpoint
    #         if response_id == '10':
    #             if return_values[0] == '$':
    #                 pass
    #             elif return_values[0] == '1':
    #                 raise ValueError('Anode voltage setpoint out of range!')
    #             else:
    #                 raise RuntimeError
                
    #         # Parse response for changing anode current setpoint
    #         elif response_id == '11':
    #             if return_values[0] == '$':
    #                 pass
    #             elif return_values[0] == '1':
    #                 raise ValueError('Anode current setpoint out of range!')
    #             else:
    #                 raise RuntimeError
                
    #         # Parse response for changing filament preheat current setpoint
    #         elif response_id == '12':
    #             if return_values[0] == '$':
    #                 pass
    #             elif return_values[0] == '1':
    #                 raise ValueError('Filament preheat current out of range!')
    #             else:
    #                 raise RuntimeError
                
    #         # Parse response for changing filament current limit setpoint
    #         elif response_id == '13':
    #             if return_values[0] == '$':
    #                 pass
    #             elif return_values[0] == '1':
    #                 raise ValueError('Filament current limit out of range!')
    #             else:
    #                 raise RuntimeError
                
    #         # Parse anode voltage setpoint
    #         elif response_id == '14':
    #             self.voltage_setpoint = int(return_values[0])*self._voltage_setpoint_res
                
    #         # Parse anode current setpoint
    #         elif response_id == '15':
    #             self.current_setpoint = int(return_values[0])*self._current_setpoint_res
                
    #         # Parse filament preheat current setpoint
    #         elif response_id == '16':
    #             self.fil_current_setpoint = int(return_values[0])*self._fil_current_setpoint_res
                
    #         # Parse filament current limit setpoint
    #         elif response_id == '17':
    #             self.fil_maxcurrent = int(return_values[0])*self._fil_current_setpoint_res
                
    #         # Parse analog readback values    
    #         elif response_id == '20':
    #             ''' Workaround for strange bug. After reenabling HV manually the 
    #             response to requesting the readback values is missing one value.
    #             This workaround will ignore the initial wrong reading. Which value
    #             is missing will be investigated soon. Possible values are marked with '?'
    #             '''
    #             if len(return_values) == 7:
    #                 self.lv_board_temp = int(return_values[0]) * self._lv_temp_res
    #                 self.lv_supply_voltage = int(return_values[1]) * self._lv_supply_voltage_res
    #                 self.voltage = int(return_values[2]) * self._voltage_res
    #                 self.current = int(return_values[3]) * self._current_res            # ?
    #                 self.fil_current = int(return_values[4]) * self._fil_current_res    # ?
    #                 self.fil_voltage = int(return_values[5]) * self._fil_voltage_res    # ?
    #                 self.hv_board_temp = int(return_values[6]) * self._hv_temp_res
                    
    #             else:
    #                 print('received wrong response to analog readback request.')
    #                 self.lv_board_temp = int(return_values[0]) * self._lv_temp_res
    #                 self.lv_supply_voltage = int(return_values[1]) * self._lv_supply_voltage_res
    #                 self.voltage = int(return_values[2]) * self._voltage_res
    #                 # Due to the bug hv_board_temp_value is at list index 5
    #                 self.hv_board_temp = int(return_values[5]) * self._hv_temp_res
                    
    #         # Parse total hours HV On
    #         elif response_id == '21':
    #             self.hv_on_hours = float(return_values[0])
                
    #         # Parse status request
    #         elif response_id == '22':
    #             self.hv_on = bool(strtobool(return_values[0]))
    #             self.interlock_open = bool(strtobool(return_values[1]))
    #             self.fault = bool(strtobool(return_values[2]))
                
                
    #         # Parse software version
    #         elif response_id == '23':
    #             self.sw_version = return_values[0]
                
    #         # Parse hardware version   
    #         elif response_id == '24':
    #             self.hw_version = return_values[0]
                
    #         # Parse model number
    #         elif response_id == '26':
    #             self.model_number = return_values[0]
                
    #         # Parse response to resetting on hours counter
    #         elif response_id == '30':
    #             if return_values[0] == '$':
    #                 pass
    #             else:
    #                 raise RuntimeError
                
    #         # Parse response to expanded status request
    #         elif response_id == '32':
    #             self.hv_on = bool(strtobool(return_values[0]))
    #             self.interlock_open = bool(strtobool(return_values[1]))
    #             self.interlock_fault = bool(strtobool(return_values[2]))
    #             self.overvoltage_fault = bool(strtobool(return_values[3]))
    #             self.configuration_fault = bool(strtobool(return_values[4]))
    #             self.overpower_fault = bool(strtobool(return_values[5]))
    #             self.lv_undervoltage_fault = bool(strtobool(return_values[6]))
                
    #         # Parse response to change filament ramptime request
    #         elif response_id == '47':
    #             if return_values[0] == '$':
    #                 pass
    #             elif return_values[0] == '1':
    #                 raise ValueError('Filament ramp time out of range!')
    #             else:
    #                 raise RuntimeError
                
    #         # Parse filament ramptime
    #         elif response_id == '48':
    #             self.fil_ramp_enabled = bool(strtobool(return_values[0]))
    #             self.fil_ramptime = int(return_values[1])
                
    #         # Parse response to reset faults request
    #         elif response_id == '52':
    #             if return_values[0] == '$':
    #                 pass
    #             else:
    #                 raise RuntimeError
                
    #         # Parse auxiliary kV feedback
    #         elif response_id == '65':
    #             self.aux_voltage = int(return_values[0]) * self._aux_voltage_res
                
    #         # Parse SVN revision
    #         elif response_id == '66':
    #             self.svn_version = return_values[0]
            
    #         # Read digital inputs
    #         elif response_id == '76':
    #             self.hv_on = bool(strtobool(return_values[0]))
    #             self.interlock_open = bool(strtobool(return_values[1]))
    #             self.local_remote = bool(strtobool(return_values[2]))
    #             self.overvoltage_fault = bool(strtobool(return_values[3]))
    #             self.overcurrent_fault = bool(strtobool(return_values[4]))
    #             self.reg_fault = bool(strtobool(return_values[5]))
    #             self.arc_occured = bool(strtobool(return_values[6]))
    #             self.temp_fault = bool(strtobool(return_values[7]))
                
            
    #         # Parse response to HV on/off request
    #         elif response_id == '99':
    #             if return_values[0] == '$':
    #                 pass
    #             elif return_values[0] == '1':
    #                 raise ValueError('Wrong argument. Must be 0 or 1.')
    #             elif return_values[0] == '2':
    #                 raise ValueError('Can\'t enable HV. Interlock open.')
    #             else:
    #                 raise RuntimeError
                    
    #         else:
    #             pass
                
    #####################
    # Functions for modifying setpoints
    #####################
    def set_voltage(self, voltage):
        write_config_value('SETPOINTS','voltage',str(voltage))
        return
        
    def set_current(self, current):
        write_config_value('SETPOINTS','current',str(current))
        return
        
    def set_fil_preheat(self, preheat):
        write_config_value('SETPOINTS','fil_current',str(preheat))
        return
    def set_fil_maxcurrent(self, maxcurrent):
        write_config_value('SETPOINTS','fil_maxcurrent',str(maxcurrent))
        return
        
    def enable_hv(self):
        write_config_value('STATES','hv_on',str(True))
        return
        
    def disable_hv(self):
        write_config_value('STATES','hv_on',str(False))
        return
        
    def reset_faults(self):
        pass
        
    def reset_hours(self):
        pass

        
        
class spellman_MNX(spellman):
    # Same across all MNX models. Model specific constants are handled in the corresponding child classes.
    # DAC resolutions for setpoints
    _fil_current_setpoint_res = 2.442
    
    # ADC resolutions for feedback
    _fil_current_res = 0.87912
    _fil_voltage_res = 0.001343
    _lv_supply_voltage_res = 0.010476
    _lv_temp_res = 0.07326
    _hv_temp_res = 0.07326
    
    # definition of MNX supported commands for device information
    _device_info_commands = {'hv_on_hours': '21', 'sw_version': '23,', 'hw_version': '24,', 'model_number': '26,'}
    
    # definition of MNX series specific commands used by the auto updater
    _readback_getter_commands = {'analog_readback': '20,', 'status': '22,', 'digital': '76,'}
    _setpoint_getter_commands = {'voltage_setpoint': '14,', 'current_setpoint': '15,', 'fil_current_setpoint': '16,', 'fil_maxcurrent': '17,'}
    
    def __init__(self, HOST, PORT):
        super().__init__(HOST, PORT)
        
        
class spellman_uXMAN(spellman):
    # Same across all uXMAN models. Model specific constants are handled in the corresponding child classes.
    # DAC resolutions for setpoints
    _fil_current_setpoint_res = 2.442
    
    # ADC resolutions for feedback
    _fil_current_res = 0.87912
    _fil_voltage_res = 0.001343
    _lv_supply_voltage_res = 0.010476
    _lv_temp_res = 0.07326
    _hv_temp_res = 0.07326
    
    # definition of uXMAN supported commands for device information
    _device_info_commands = {}#{'hv_on_hours': '21', 'sw_version': '23,', 'hw_version': '24,', 'model_number': '26,', 'svn_version': '66,'}
    
    # definition of uXMAN supported commands used by the auto updater
    _readback_getter_commands = {'analog_readback': '20,'}#, 'expanded_status': '32,'}
    _setpoint_getter_commands = {'voltage_setpoint': '14,', 'current_setpoint': '15,', 'fil_current_setpoint': '16,', 'fil_maxcurrent': '17,'}#, 'aux_kv_feedback': '65,', 'fil_ramptime': '47,'}
    
    def __init__(self, HOST, PORT):
        super().__init__(HOST, PORT)
        
    def set_fil_ramptime(self, ramptime, enabled=True):
        # ToDo: check for max value
        cmd_id = '47'
        #
        commandstring = ''.join([cmd_id, ',', str(int(enabled)), ',', str(ramptime), ','])
        self.sendqueue.put(commandstring)
        
        
class spellman_MNX50P50(spellman_MNX):
    # Model specific constants
    # DAC resolutions for setpoints
    _voltage_setpoint_res = 12.21
    _current_setpoint_res = 0.4884
    
    # ADC resolutions for feedback
    _voltage_res = 12.21
    _current_res = 0.5861
    
    def __init__(self, HOST='192.168.1.4', PORT=50001):
        super().__init__(HOST, PORT)
        
        
class spellman_uX50P50(spellman_uXMAN):
    # Model specific constants
    # DAC resolutions for setpoints
    _voltage_setpoint_res = 12.21
    _current_setpoint_res = 0.4884
    
    # ADC resolutions for feedback
    _voltage_res = 12.21
    _current_res = 0.5861
    _aux_voltage_res = 13.43
    
    def __init__(self, HOST='192.168.1.4', PORT=50001):
        super().__init__(HOST, PORT)
        
        
if __name__ == '__main__':

    a = spellman_uX50P50('127.0.0.1', 50001)
    
    while(True):
        try:
            voltage = float(input('Spannung...\n'))
            a.set_voltage(voltage)
            print(a.voltage)
            time.sleep(2)

        except KeyboardInterrupt:
            a.connection.close()
            sys.exit()
