#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This file simulates the reaction of the source when changing the
# current and the voltage
import time
from configparser import ConfigParser
from distutils.util import strtobool
import random


PATH_CONFIG_FILE = "config.ini"

# def load_config_value(category,name):
#     config_object = ConfigParser()
#     config_object.read(PATH_CONFIG_FILE)
#     return config_object[category][name]

# def write_config_value(category,name,value_string):
#     config_object = ConfigParser()
#     config_object.read(PATH_CONFIG_FILE)
#     config_object[category][name] = value_string
#     with open(PATH_CONFIG_FILE, 'w') as configfile:
#         config_object.write(configfile)
#     return None

while True:
    # Load config object
    config_object = ConfigParser()
    config_object.read(PATH_CONFIG_FILE)
    
    voltage_setpoint = float(config_object['SETPOINTS']['voltage'])
    current_setpoint = float(config_object['SETPOINTS']['current'])
    hv_on = bool(strtobool(config_object['STATES']['hv_on']))
    if hv_on:
        config_object['FEEDBACK']['current'] = str(current_setpoint * (1+(random.random()-0.5)*0.1))
        config_object['FEEDBACK']['voltage'] = str(voltage_setpoint * (1+(random.random()-0.5)*0.1))
    else:
        config_object['FEEDBACK']['current'] = str(0)
        config_object['FEEDBACK']['voltage'] = str(0)    
    
    with open(PATH_CONFIG_FILE, 'w') as configfile:
        config_object.write(configfile)
    
    time.sleep(0.5)


