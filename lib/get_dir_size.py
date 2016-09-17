#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:get_dir_size.py
@time(UTC+8):16/9/15-22:27
'''
import os


def get_dir_size(dir_abs_path):
    if not os.path.isabs(dir_abs_path):
        print("args should be a absolute path")
        return
    else:
        size = 0
        for root, dirs, files in os.walk(dir_abs_path):
            size += sum([os.path.getsize(os.path.join(root, file)) for file in files])
        return size

if __name__ == '__main__':
    res = get_dir_size("/data/yangli.d/")
    print(res)
