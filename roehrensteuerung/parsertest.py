# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 18:03:28 2022

@author: mail
"""
from configparser import ConfigParser
from distutils.util import strtobool


config_object = ConfigParser()

#%%

#Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")

#Get the password["HV_on"]
userinfo = config_object["STATES"]
print("Password is {}".format(userinfo["HV_on"]))

#%%
config_object["FEEDBACK"]["fil_current"] = '10.0'
with open("config.ini", 'w') as configfile:
    config_object.write(configfile)
    
    
    
#%%

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

#%%
print(bool(strtobool(load_config_value('STATES','fault'))))

#%%
write_config_value(['STATES'],['fault'],'1.0')