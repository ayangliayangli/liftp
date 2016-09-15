#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:my_subprocess.py
@time(UTC+8):16/9/13-22:32
'''
import subprocess


def execute_cmd(cmd, cwd=""):

    res = subprocess.Popen(cmd, shell=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           cwd=cwd,
                           )
    res_data_bytes = res.stdout.read()
    if not res_data_bytes:
        res_data_bytes = res.stderr.read()
    if not res_data_bytes:
        res_data_str = "cmd execute success , but no output"
        res_data_bytes = bytes(res_data_str, encoding='utf-8')
    return res_data_bytes




# 下方是测试函数
def test_rm_dir():
    res = subprocess.Popen("rm -rf null2.d", shell=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           cwd="/data/yangli.d/",
                           )
    print(res.stdout.read())
    print(res.stderr.read())

if __name__ == '__main__':
    test_rm_dir()
