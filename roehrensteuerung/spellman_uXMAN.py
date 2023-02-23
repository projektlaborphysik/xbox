#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import sys
import socket
from threading import Thread, Event
from queue import Queue
from distutils.util import strtobool
Start = b'\x02'
End = b',\x03'


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


class spellman_uX:
    
    # Same across all models. Model specific constants are handled in the corresponding child classes.
    # DAC resolutions for setpoints
    _fil_current_setpoint_res = 2.442
    
    # ADC resolutions for feedback
    _fil_current_res = 0.87912
    _fil_voltage_res = 0.001343
    _temp_res = 0.07326
    _lv_supply_voltage_res = 0.010476
    _temp_sensor_res = 0.07326
    
    _device_info_commands = {'hv_on_hours': '21', 'sw_version': '23,', 'hw_version': '24,', 'model_number': '26,', 'svn_version': '66,'}
    _readback_getter_commands = {'analog_readback': '20,', 'expanded_status': '32,'}
    _setpoint_getter_commands = {'voltage_setpoint': '14,', 'current_setpoint': '15,', 'fil_current_setpoint': '16,', 'fil_maxcurrent': '17,', 'aux_kv_feedback': '65,', 'fil_ramptime': '47,'}
    
    
    def __init__(self, HOST, PORT):
        
        # Ethernet connection
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.connection.connect((HOST, PORT))
        
        except socket.error as exc:
            print('Socket error: %s' % exc)
            sys.exit()
        
        self.sendqueue = Queue()
        self.receivequeue = Queue()
        
        self.receiver = Thread(target=self._receive_ethernet)
        self.receiver.daemon = True
        self.receiver.start()
        
        self.sender = Thread(target=self._send_ethernet)
        self.sender.daemon = True
        self.sender.start()
        
        self.parser = Thread(target=self._parse_response)
        self.parser.daemon = True
        self.parser.start()
        
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
        
        
    #####################
    # Functions for communication via Ethernet
    #####################
    def _send_ethernet(self):
        while True:
            commandstring = self.sendqueue.get()
            message = ''.join(['\x02', commandstring, '\x03'])
            try:
                self.connection.sendall(message.encode())
                time.sleep(0.005)
            except socket.error as exc:
                print('Could not send command: %s' % exc)
                self._stop()
                sys.exit()
                
                
    def _stop(self):
        self.readback_updater.join()
        self.setpoint_updater.join()
        
        self.receiver.join()
        self.sender.join()
        self.parser.join()
    
    
    def _receive_ethernet(self):
        while True:
            # read from interface
            responses = []
            frame = self.connection.recv(1024)
            
            # search for start of response
            if Start in frame:
                
                # handle possible multiple responses in one frame
                responses = frame.split(Start)[1:]
                
                for response in responses:
                    # check if response is properly terminated
                    if End in response:
                        tmp, *_ = response.split(End)
                        self.receivequeue.put(tmp.decode())
                    else:
                        pass
                        
                        
    def _update_readbacks(self):
        for i in self._readback_getter_commands.keys():
            self.sendqueue.put(self._readback_getter_commands[i])
        return
        
        
    def _update_setpoints(self):
        for i in self._setpoint_getter_commands.keys():
            self.sendqueue.put(self._setpoint_getter_commands[i])
        return
        
        
    def _parse_response(self):
        while True:
            response_string = self.receivequeue.get()
            print(response_string)
            response_id, *return_values = response_string.split(',')
            
            # Parse response for changing anode voltage setpoint
            if response_id == '10':
                if return_values[0] == '$':
                    pass
                elif return_values[0] == '1':
                    raise ValueError('Anode voltage setpoint out of range!')
                else:
                    raise RuntimeError
                
            # Parse response for changing anode current setpoint
            elif response_id == '11':
                if return_values[0] == '$':
                    pass
                elif return_values[0] == '1':
                    raise ValueError('Anode current setpoint out of range!')
                else:
                    raise RuntimeError
                
            # Parse response for changing filament preheat current setpoint
            elif response_id == '12':
                if return_values[0] == '$':
                    pass
                elif return_values[0] == '1':
                    raise ValueError('Filament preheat current out of range!')
                else:
                    raise RuntimeError
                
            # Parse response for changing filament current limit setpoint
            elif response_id == '13':
                if return_values[0] == '$':
                    pass
                elif return_values[0] == '1':
                    raise ValueError('Filament current limit out of range!')
                else:
                    raise RuntimeError
                
            
            # Parse anode voltage setpoint
            elif response_id == '14':
                self.voltage_setpoint = int(return_values[0])*self._voltage_setpoint_res
                
            # Parse anode current setpoint
            elif response_id == '15':
                self.current_setpoint = int(return_values[0])*self._current_setpoint_res
                
            # Parse filament preheat current setpoint
            elif response_id == '16':
                self.fil_current_setpoint = int(return_values[0])*self._fil_current_setpoint_res
                
            # Parse filament current limit setpoint
            elif response_id == '17':
                self.fil_maxcurrent = int(return_values[0])*self._fil_current_setpoint_res
                
            # Parse analog readback values    
            elif response_id == '20':
                self.lv_board_temp = int(return_values[0]) * self._temp_sensor_res
                self.lv_supply_voltage = int(return_values[1]) * self._lv_supply_voltage_res
                self.voltage = int(return_values[2]) * self._voltage_res
                self.current = int(return_values[3]) * self._current_res
                self.fil_current = int(return_values[4]) * self._fil_current_res
                self.fil_voltage = int(return_values[5]) * self._fil_voltage_res
                self.hv_board_temp = int(return_values[6]) * self._temp_res
                
            # Parse total hours HV On
            elif response_id == '21':
                self.hv_on_hours = float(return_values[0])
                
            # Parse status request
            elif response_id == '22':
                self.hv_on = bool(strtobool(return_values[0]))
                self.interlock_open = bool(strtobool(return_values[1]))
                self.fault = bool(strtobool(return_values[2]))
                
                
            # Parse software version
            elif response_id == '23':
                self.sw_version = return_values[0]
                
            # Parse hardware version   
            elif response_id == '24':
                self.hw_version = return_values[0]
                
            # Parse model number
            elif response_id == '26':
                self.model_number = return_values[0]
                
            # Parse response to resetting on hours counter
            elif response_id == '30':
                if return_values[0] == '$':
                    pass
                else:
                    raise RuntimeError
                
            # Parse response to expanded status request
            elif response_id == '32':
                self.hv_on = bool(strtobool(return_values[0]))
                self.interlock_open = bool(strtobool(return_values[1]))
                self.interlock_fault = bool(strtobool(return_values[2]))
                self.overvoltage_fault = bool(strtobool(return_values[3]))
                self.configuration_fault = bool(strtobool(return_values[4]))
                self.overpower_fault = bool(strtobool(return_values[5]))
                self.lv_undervoltage_fault = bool(strtobool(return_values[6]))
                
            # Parse response to change filament ramptime request
            elif response_id == '47':
                if return_values[0] == '$':
                    pass
                elif return_values[0] == '1':
                    raise ValueError('Filament ramp time out of range!')
                else:
                    raise RuntimeError
                
            # Parse filament ramptime
            elif response_id == '48':
                self.fil_ramp_enabled = bool(strtobool(return_values[0]))
                self.fil_ramptime = int(return_values[1])
                
            # Parse response to reset faults request
            elif response_id == '52':
                if return_values[0] == '$':
                    pass
                else:
                    raise RuntimeError
                
            # Parse auxiliary kV feedback
            elif response_id == '65':
                self.aux_voltage = int(return_values[0]) * self._aux_voltage_res
                
            # Parse SVN revision
            elif response_id == '66':
                self.svn_version = return_values[0]
                
            # Parse response to HV on/off request
            elif response_id == '99':
                if return_values[0] == '$':
                    pass
                elif return_values[0] == '1':
                    raise ValueError('Wrong argument. Must be 0 or 1.')
                elif return_values[0] == '2':
                    raise ValueError('Can\'t enable HV. Interlock open.')
                else:
                    raise RuntimeError
                    
            else:
                pass
                
                
    #####################
    # Functions for modifying setpoints
    #####################
    
    def set_voltage(self, voltage):
        cmd_id = '10'
        #
        try:
            dac_value = int(round(voltage / self._voltage_setpoint_res))
            
            if dac_value not in range(4096):
                raise ValueError('Voltage %2.1f V out of range.' % voltage)
        
        except ValueError as exc:
            print('ValueError: %s' % exc)
            return
            
        commandstring = ''.join([cmd_id, ',', str(dac_value), ','])
        self.sendqueue.put(commandstring)
        
        
    def set_current(self, current):
        cmd_id = '11'
        #
        try:
            dac_value = int(round(current / self._current_setpoint_res))
            
            if dac_value not in range(4096):
                raise ValueError('Current %2.1f mA out of bounds.' % current)
        
        except ValueError as exc:
            print('ValueError: %s' % exc)
            return
            
        commandstring = ''.join([cmd_id, ',', str(dac_value), ','])
        self.sendqueue.put(commandstring)
        
        
    def set_fil_preheat(self, preheat):
        cmd_id = '12'
        #
        try:
            dac_value = int(round(preheat / self._fil_current_setpoint_res))
            
            if dac_value not in range(4096):
                raise ValueError('Current %2.1f mA out of bounds.' % preheat)
        
        except ValueError as exc:
            print('ValueError: %s' % exc)
            return
            
        commandstring = ''.join([cmd_id, ',', str(dac_value), ','])
        self.sendqueue.put(commandstring)
        
        
    def set_fil_maxcurrent(self, maxcurrent):
        cmd_id = '13'
        #
        try:
            dac_value = int(round(maxcurrent / self._fil_current_setpoint_res))
            
            if dac_value not in range(4096):
                raise ValueError('Current %2.1f mA out of bounds.' % maxcurrent)
        
        except ValueError as exc:
            print('ValueError: %s' % exc)
            return
            
        commandstring = ''.join([cmd_id, ',', str(dac_value), ','])
        self.sendqueue.put(commandstring)
        
        
    def set_fil_ramptime(self, ramptime, enabled=True):
        # ToDo: check for max value
        cmd_id = '47'
        #
        commandstring = ''.join([cmd_id, ',', str(int(enabled)), ',', str(ramptime), ','])
        self.sendqueue.put(commandstring)   
        
    def enable_hv(self):
        cmd_id = '99'
        #
        commandstring = ''.join([cmd_id, ',', str(1), ','])
        self.sendqueue.put(commandstring)
        
        
    def disable_hv(self):
        cmd_id = '99'
        #
        commandstring = ''.join([cmd_id, ',', str(0), ','])
        self.sendqueue.put(commandstring)
        
        
    def reset_faults(self):
        cmd_id = '52'
        #
        commandstring = ''.join([cmd_id, ','])
        self.sendqueue.put(commandstring)
        
        
    def reset_hours(self):
        cmd_id = '30'
        #
        commandstring = ''.join([cmd_id, ','])
        self.sendqueue.put(commandstring)
        
        
class spellman_uX50P50(spellman_uX):
    # Model specific constants
    # DAC resolutions for setpoints
    _voltage_setpoint_res = 12.21
    _current_setpoint_res = 0.4884
    
    # ADC resolutions for feedback
    _voltage_res = 12.21
    _aux_voltage_res = 13.43
    _current_res = 0.58608
    
    
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
