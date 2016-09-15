#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:test_rm_dir.py
@time(UTC+8):16/9/14-14:28
'''

from lib import my_subprocess

res_bytes = my_subprocess.execute_cmd("rm -rf dfdf.d", "/data/yangli.d")
print(res_bytes)

