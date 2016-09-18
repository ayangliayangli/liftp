#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:ftp_server.py
@time(UTC+8):16/9/12-15:19
'''

import os, sys
import subprocess
import socketserver
import json
import configparser
from lib import my_progress
from lib import myhash
from src import handle_cmd_server
from src import user_admin
from src.user_admin import User  # User is a class, 当使用另一个模块的类的时候,要显示的导入该类,否则无法执行里面的静态方法
from config import setting



class MyServer(socketserver.BaseRequestHandler):
    welcome_msg_template_str = '''
                        welcome {}
                        this is ftp server via python3
                        write by yangli
                        yangliw3@foxmail.com
                        '''

    def handle(self):
        logined_user = ""  # 已经登录的用户的信息
        user_home_dir = ""
        user_chroot_flag = False

        conn = self.request
        client_info = self.client_address

        # return welcome message  -------------
        print("{} is connected".format(client_info))
        welcome_msg_str = MyServer.welcome_msg_template_str.format(client_info)
        print("-------", welcome_msg_str)
        conn.send(bytes(welcome_msg_str, encoding='utf-8'))

        # logined process --------------------
        while not logined_user:
            # recv_data_dic = {"name":"***", "password":"***"}
            # logined_user = "1"
            recv_data_bytes = conn.recv(1024)
            recv_data_dic = json.loads(str(recv_data_bytes, encoding='utf-8'))
            auth_res = User.login(recv_data_dic["name"], recv_data_dic["password"])
            # auth_res2 = User.login('yangli', '123456')

            # 构造要返回给客户端的数据,如果验证成功还有wd  chroot 两个key
            send_data_dict = {"status":auth_res, "wd":"", "chroot":""}

            if auth_res == 1:
                # login success
                logined_user = recv_data_dic["name"]  # logined user name

                # 去配置文件里面拿到用户的家目录和chroot flag
                config = configparser.ConfigParser()
                config.read(setting.LIFTP_CONFIG_FILE_PATH, encoding='utf-8')
                user_home_dir = config.get(logined_user, "home")
                user_chroot_flag = config.get(logined_user, "chroot")

                # 补充要返回给客户端的数据
                send_data_dict["wd"] = user_home_dir
                send_data_dict["chroot"] = user_chroot_flag

                # 发送数据给客户端
                send_data_json = json.dumps(send_data_dict)
                conn.send(bytes(send_data_json, encoding='utf-8'))

                break  # 验证成功,跳出循环
            elif auth_res == 2:
                # password is wrong
                print("password is wrong")
            elif auth_res == 3:
                print("user is not exist")
            else:
                print("user_admin.User.login return wrong ")

            # 发送数据给客户端, 默认情况下也是要发送的,只是数据不完整,wd  chroot 这两个key内容为空
            send_data_json = json.dumps(send_data_dict)
            conn.send(bytes(send_data_json, encoding='utf-8'))



        while True:
            # 循环接收命令  -------------------

            # 开始接收文件信息
            print("li---", "开始接收命令信息")
            recv_data_bytes = conn.recv(1024)  # blocking for a wihle
            print("li---", "结束接收命令信息")
            recv_data_dic = json.loads(str(recv_data_bytes, encoding='utf-8'))
            print(type(recv_data_dic), recv_data_dic)

            # 给客户端发送确认信息, 这个很重要,否则会出现粘包
            conn.send(bytes('ready', encoding='utf-8'))

            # 客户端不同的命令,去调用不通的服务器端的方法来执行相应的请求
            # e.g. put ls get cd
            # 利用python 反射
            cmd_request = "cmd_" + str(recv_data_dic["cmd"])
            if hasattr(handle_cmd_server, cmd_request):
                func = getattr(handle_cmd_server, cmd_request)
                func(recv_data_dic, conn, logined_user)


    def setup(self):
        super(MyServer, self).setup()

    def finish(self):
        super(MyServer, self).finish()


def main():
    ip_port = ('0.0.0.0', 8888)
    myServer = socketserver.ThreadingTCPServer(ip_port, MyServer)
    print("server is running ... ")
    myServer.serve_forever()

if __name__ == '__main__':
    main()