#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:test_user_admin.py
@time(UTC+8):16/9/13-17:07
'''

from src.user_admin import User

# user_null = user_admin.User()
# res = user_null.login("yangli","123456")
res = User.login("yangli", "123456")

print(res)