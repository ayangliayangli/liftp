#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:setting.py
@time(UTC+8):16/9/12-15:51
'''
import os, sys

# 加密用户使用的密钥,用户可以自行更改
PASSWORD_KEY = "123456"

# 醒目的家目录
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 用户名和密码保存路径
USER_INFO_FILE_PATH = os.path.join(PROJECT_PATH, "db", "user_info.db")

# ftp主配置文件路径
LIFTP_CONFIG_FILE_PATH = os.path.join(PROJECT_PATH, "config", "liftp.conf")