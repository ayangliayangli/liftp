#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:myhash.py
@time(UTC+8):16/9/12-15:53
'''

import hashlib, os
from config import setting


def hash_sha256_with_file(file_abspath):
    print("-li--: compute sha256 for {} ... ".format(file_abspath))
    if os.path.isabs(file_abspath):
        # 给的是绝对路径,开始读取文件处理
        with open(file_abspath, 'rb') as fp :
            file_content_bytes = fp.read()
            my_hash = hashlib.sha256()
            my_hash.update(file_content_bytes)
            res = my_hash.hexdigest()
            return res
    else:
        # 给的参数不是一个绝对路径
        print("need give a absolute file path")
        return False


def hash_sha256_with_string(str):
    # 使用了配置文件里面的加密密钥,进一步增加文件系统的安全性

    myhash = hashlib.sha256(bytes(setting.PASSWORD_KEY, encoding='utf-8'))
    myhash.update(bytes(str, encoding='utf-8'))
    res = myhash.hexdigest()
    return res

if __name__ == '__main__':
    # file_abspath = os.path.abspath(__file__)
    # res = hash_sha256_with_file("22")
    # print(res)

    print(hash_sha256_with_string("12345678"))

