#!/usr/bin/env python3

import configparser as ConfigParser
import os
import io
import logger

filepath = "/share/Helpers/settings.ini"

"""
    Gets a configuration value from the settings file
"""
def get_value(section, name):
    try:
        config = ConfigParser.ConfigParser()
        config.read(filepath)
        return config[section][name]
    except Exception as e:
        logger.error(str(e))

"""
    Sets a configuration value in the settings file
"""
def set_value(section, name, value):
    try:
        config = ConfigParser.ConfigParser()
        config.read(filepath)
        config[str(section)][str(name)] = str(value)
        with open(filepath, 'w') as configfile:
            config.write(configfile)
    except Exception as e:
        logger.error(str(e))
