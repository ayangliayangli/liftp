#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:util_pickle.py
@time(UTC+8):16/9/13-14:15
'''

import pickle


def write_obj_to_file_with_pickle(obj, abs_path):
    with open(abs_path, "wb") as fp:
        pickle.dump(obj, fp)


def read_obj_from_file_with_pickle(abs_path):
    with open(abs_path, 'rb') as fp:
        obj = pickle.load(fp)
        return obj
