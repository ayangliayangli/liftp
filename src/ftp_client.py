#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:ftp_client.py
@time(UTC+8):16/9/12-15:19
'''

import os, sys
import json
import subprocess
import socketserver, socket
from lib import myhash
from src import handle_cmd_client

# var scop
logined_user = ""
work_direction = ""
chroot_flag = False


def show_help():
    s = '''
        ls                          -- list current work direction simple
        ll                          -- list current work direction with long mode
        mkdir dir                   -- make dir
        rm dir/filename             -- remove dir or remove filename
        cd dir/..                   -- change work direction to [dir] or parrent dir [..]
        put localfile [server_dir]  -- put localfile to server dir, [server_dir] is optional, current work direction is default
        get serverfile local_dir    -- get serverfile to local direction

    '''
    print(s)


def login(my_sock):
    print("you should login first, if you do not have account , contact administrator")
    while not logined_user:
        # 未登录的情况
        name = input("name:").strip()
        password = input("password:").strip()
        user_info_dict = {"name":name, "password":password}
        user_info_json = json.dumps(user_info_dict)
        my_sock.send(bytes(user_info_json, encoding="utf-8"))  # 发送登录信息
        auth_res_dict = json.loads(str(my_sock.recv(1024), encoding='utf-8'))  # 接受返回结果
        auth_res_status_code = int(auth_res_dict["status"])
        auth_res_work_direction = auth_res_dict["wd"]
        auth_res_chroot_flag = auth_res_dict["chroot"]

        if  auth_res_status_code == 1:
            print("{} login success".format(name))
            global logined_user
            global work_direction
            global chroot_flag
            logined_user = name  # 把当前登录用户信息放在全局变量中
            work_direction = auth_res_work_direction  # 当前工作目录
            chroot_flag = auth_res_chroot_flag  # 是否允许改变家目录的标志位
            show_help()  # show help information
            break  # 登录成功跳出循环
        elif auth_res_status_code == 2:
            print("user:{} password is wrong".format(name))
            continue
        elif auth_res_status_code == 3:
            print("user:{} is not exist".format(name))
            continue
        else:
            print("auth_res return wrong")
            continue


def main():
    ip = '127.0.0.1'
    port = 8888
    ip_port = (ip, port)

    my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_sock.connect(ip_port)

    # received welcome infomation
    recv_data_bytes = my_sock.recv(1024)
    print(str(recv_data_bytes, encoding='utf-8'))

    # 用户登录
    login(my_sock)  # 登录成功后,会把相应的用户信息放入全局变量中

    while True:
        while True:
            # 获取正确的输入cmd
            notification_str = "{}@{} {}>>:".format(logined_user, ip_port[0], work_direction)
            cmd = input(notification_str).strip()
            if cmd == "": continue
            cmd_list = cmd.split(" ")
            cmd_first = "cmd_" + cmd_list[0]  # put ---> cmd_put

            if cmd_first == "cmd_put":
                if len(cmd_list) < 2 or len(cmd_list) > 3:
                    # 输入命令错误,重新输入
                    print("USAGE: put sorce_file_path  dist_file_path")
                    print("USAGE: put sorce_file_path")
                    continue
                else:
                    if len(cmd_list) == 2: cmd_list.append("") # 如果没有指定server path,那就默认当前目录
                    break
            elif cmd_first == "cmd_cd":
                if len(cmd_list) < 2:
                    print("USAGE: cd ..")
                    print("USAGE: cd dir_name")
                    continue
                else:
                    break
            elif cmd_first == 'cmd_ls' or cmd_first == "cmd_ll":
                if len(cmd_list) > 1:
                    print("USAGE: ls ")
                    continue
                else:
                    break
            elif cmd_first == "cmd_mkdir" or cmd_first == "cmd_rm":
                if len(cmd_list) == 2:
                    break
                else:
                    print("USEAGE: mkdir dir")
                    print("USEAGE: rm filename/dirmane")
                    continue
            elif cmd_first == "cmd_get":
                if len(cmd_list) == 3:
                    break
                else:
                    print("USEAGE: get remote_file local_dir")
            elif cmd_first == "cmd_help" or cmd_first == 'cmd_?':
                show_help()
            else:
                print("{} comming soon perhaps".format(cmd_list[0]))

        # 开始执行命令
        if hasattr(handle_cmd_client, cmd_first):
            # 如果又这个函数, 比如cmd_put
            f = getattr(handle_cmd_client, cmd_first)
            res = f(cmd_list, my_sock, work_direction)

            if res:
                print("-----execute success")

            if cmd_first == 'cmd_cd': # 要处理返回值, 给work_direction

                global work_direction
                work_direction = dict(res).get("wd", work_direction)  # change work direction according to res by cmd_cd()
                msg = dict(res).get("msg", "")
                print(msg)  # print change work direction message


def cmd_cd(relate_path):
    pass


if __name__ == '__main__':  # program interface
    main()


