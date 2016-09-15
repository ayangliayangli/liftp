#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:test_configParser.py
@time(UTC+8):16/9/13-17:43
'''

from config import setting
import configparser

config = configparser.ConfigParser()
config.read(setting.LIFTP_CONFIG_FILE_PATH, encoding='utf-8')
print(config.sections())
print(config.options("yangli"))
print(config.get("yangli", "home"))