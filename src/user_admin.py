#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:user_admin.py
@time(UTC+8):16/9/13-14:12
'''

from config import setting
from lib import util_pickle
from lib import myhash


class User():
    # 所有用户的信息会放在dict中, key--> name value--> user
    # {"yanlgi": yangli, "dujuan": dujuan}

    def __init__(self, name="", password=""):
        self.name = name
        self.password = password

    def __str__(self):
        s = '''
            ----------------------------------
            name:{}
            password:{}
            '''.format(self.name, self.password)
        return s

    @staticmethod
    def fetch_all_user():
        try:
            obj = util_pickle.read_obj_from_file_with_pickle(setting.USER_INFO_FILE_PATH)
            return obj
        except Exception as e:
            # if exception , return a null dict
            print(e)
            return {}

    @staticmethod
    def fetch_a_user(name):
        all_user_dic = User.fetch_all_user()
        if name in all_user_dic:
            # user is exist
            return all_user_dic[name]
        else:
            # user is not exist
            print("user is not exist")
            return None

    @staticmethod
    def set_a_user():
        name = input("name:").strip()
        password = input("password:").strip()
        password_sha256_after = myhash.hash_sha256_with_string(password)
        new_user = User(name, password_sha256_after)
        # 判断user是否存在
        all_user_dic = User.fetch_all_user()
        all_user_dic.update({name:new_user})
        util_pickle.write_obj_to_file_with_pickle(all_user_dic, setting.USER_INFO_FILE_PATH)

    @staticmethod
    def login(name, password):
        # 这里传过来的密码是未加密的, 要加密后才能匹配
        # 1 -- login success
        # 2 -- password wrong
        # 3 -- user is not exist
        all_user_dict = User.fetch_all_user()
        if name in all_user_dict:
            # user is exist
            print("user is exist")
            password_sha256_after = myhash.hash_sha256_with_string(password)
            if password_sha256_after == all_user_dict[name].password:
                # password is right
                print("{} is login success".format(name))
                return 1
            else:
                # password is wrong
                print("{} password is wrong".format(name))
                return 2

        else:
            # user is not exist
            print("{} is not exist".format(name))
            return 3


if __name__ == '__main__':
    User.set_a_user()
    all_user_dict = User.fetch_all_user()
    for i in all_user_dict.values():
        print(i)

    # print(User.login("yangli", "123456"))  # --> 1



