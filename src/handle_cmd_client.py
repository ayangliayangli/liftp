#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:handle_cmd.py
@time(UTC+8):16/9/12-16:15
'''

import os
import json
from lib import myhash, my_progress


def cmd_basic_execute(*args, **kwargs):
    cmd_list = args[0]
    conn = args[1]
    work_direction = args[2]
    cmd = cmd_list[0]

    # 把当前目录和要执行的命令发送给服务端
    send_data_dic = {"cmd": cmd, "cmd_list": cmd_list, "wd": work_direction}  # 架构设计问题,cmd也要传一次,因为ls命令没有传cmd_list 过去
    conn.send(bytes(json.dumps(send_data_dic), encoding='utf-8'))

    # 等待服务器返回命令接收正确的结果  返回的结果很短,所以应该不会出现沾包
    recv_data_str = str(conn.recv(1024), encoding='utf-8')
    if recv_data_str == "ready":
        print("server have received cmd success")
        # 发送开始执行命令的信号
        conn.send(bytes('start execute cmd', encoding="utf-8"))
    else:
        print("server received cmd failure")

    # wait for server return result size
    result_data_size_str = str(conn.recv(1024), encoding='utf-8')  # bytes --> int
    print("result_data_size_str:{}".format(result_data_size_str))
    result_data_size = int(result_data_size_str)

    # tell server start trans result
    if  result_data_size :
        conn.send(bytes('start trans', encoding='utf-8'))
    else:
        print("server have not send result_data_size")

    # 等待服务器端的返回命令执行结果, 处理粘包问题
    received_data_size = 0
    received_data_bytes = b''
    while received_data_size < result_data_size:
        current_received_data_bytes = conn.recv(1024)
        received_data_bytes += current_received_data_bytes
        received_data_size += len(current_received_data_bytes)
        print('received_data_size:{} result_data_size:{}'.format(received_data_size,
                                                                 result_data_size))
    recv_data_dict = json.loads(str(received_data_bytes, encoding='utf-8'))

    # recv_data_json = str(conn.recv(1024), encoding='utf-8')
    # recv_data_dict = json.loads(recv_data_json)
    # print(recv_data_dict)

    return recv_data_dict  # return_data_dict = {"msg":"", "wd":work_direction}  # want to return data dict


def cmd_put(*args, **kwargs):
    cmd_list = args[0]
    my_sock = args[1]
    user_work_dir = args[2]
    print("start put file to server")

    # 判断本地文件是否存在
    if not os.path.exists(cmd_list[1]):
        print("file is not exist: {}".format(cmd_list[1]))
        return False

    client_file_name = os.path.basename(cmd_list[1])
    server_path = cmd_list[2]
    file_size = os.stat(cmd_list[1]).st_size
    file_hash = myhash.hash_sha256_with_file(cmd_list[1])

    file_msg_dic = {"cmd":"put",
                    "client_file_name": client_file_name,
                    "server_path": server_path,
                    "file_size": file_size,
                    "file_hash": file_hash,
                    "wd":user_work_dir, }
    file_msg_str = json.dumps(file_msg_dic)
    print("----", type(file_msg_str), file_msg_str)

    # 开始发送文件信息
    my_sock.send(bytes(file_msg_str, encoding='utf-8'))

    # wait for server ACK
    recv_data_str = str(my_sock.recv(1024), encoding='utf-8')
    if recv_data_str.startswith("ready"):

        # request quota infomation
        # server response quota info and 断电续传的信息
        # {"quota":"", "server_file_size":""}
        my_sock.send(bytes('get quota', encoding='utf-8'))
        server_quota_fexist_json = str(my_sock.recv(1024), encoding='utf-8')
        server_quota_fexist_dict = json.loads(server_quota_fexist_json)

        if server_quota_fexist_dict["quota"] == "over quota":
            print("server info: over quota ")
            return


        # 开始发送数据
        sended_size = 0
        sended_size_persents_last = 0
        with open(cmd_list[1], 'rb') as fp:
            for line in fp:
                my_sock.send(line)
                # 显示进度条,要控制显示的粒度
                sended_size += len(line)
                sended_size_persents = int(sended_size/file_size * 100)
                if sended_size_persents - sended_size_persents_last >2 or sended_size_persents == 100:
                    my_progress.show_bar(sended_size, file_size)
                    sended_size_persents_last = sended_size_persents
            print("\n-li--:sended file success")
        # 等待验证
        print("wait server check sha256 ... ")
        server_check_info_str = str(my_sock.recv(1024), encoding='utf-8')
        if server_check_info_str == "success":
            print("[ok]server check file success ...")
        elif server_check_info_str == "failure":
            print("[err]server check file failure ... ")
        else:
            print("WTF")

    return True


def cmd_ls(*args, **kwargs):
    cmd_list = args[0]
    conn = args[1]
    work_direction = args[2]
    cmd = cmd_list[0]

    # 把当前目录和要执行的命令发送给服务端
    send_data_dic = {"cmd": cmd, "wd": work_direction}
    conn.send(bytes(json.dumps(send_data_dic), encoding='utf-8'))

    # 等待服务器返回命令接收正确的结果  返回的结果很短,所以应该不会出现沾包
    recv_data_str = str(conn.recv(1024), encoding='utf-8')
    if recv_data_str == "ready":
        print("server have received cmd success")
        # 发送开始执行命令的信号
        conn.send(bytes('start execute cmd', encoding="utf-8"))
    else:
        print("server received cmd failure")

    # 等待服务器端的返回命令执行结果
    recv_data_str = str(conn.recv(1024), encoding='utf-8')
    print(recv_data_str)

    # # 给服务器返回ACK
    # conn.send(bytes('200', encoding='utf-8'))


def cmd_get(*args, **kwargs):
    cmd_list = args[0]
    conn = args[1]
    work_direction = args[2]
    cmd = cmd_list[0]
    local_file_abs_path = os.path.join(cmd_list[2], cmd_list[1])

    # 把当前目录和要执行的命令发送给服务端
    send_data_dic = {"cmd": cmd, "cmd_list": cmd_list, "wd": work_direction}  # 架构设计问题,cmd也要传一次,因为ls命令没有传cmd_list 过去
    conn.send(bytes(json.dumps(send_data_dic), encoding='utf-8'))

    # 等待服务器返回命令接收正确的结果  返回的结果很短,所以应该不会出现沾包
    recv_data_str = str(conn.recv(1024), encoding='utf-8')
    if recv_data_str == "ready":
        print("server have received cmd success")
        # 发送开始执行命令的信号
        conn.send(bytes('start execute cmd', encoding="utf-8"))
    else:
        print("server received cmd failure")

    # wait for server return server_file_info_dict
    server_file_info_json = str(conn.recv(1024), encoding='utf-8')  # bytes --> int
    server_file_info_dict = json.loads(server_file_info_json)
    server_file_size = server_file_info_dict["file_size"]
    server_file_hash = server_file_info_dict["file_hash"]

    print("result_data_size_str:{}".format(server_file_size))

    # tell server start trans result
    if  server_file_size :
        conn.send(bytes('start trans', encoding='utf-8'))
    else:
        print("server have not send result_data_size")

    # 等待服务器端的返回命令执行结果, 处理粘包问题
    # 写入文件 rb 的模式
    received_data_size = 0
    received_data_percents_last = 0

    with open(local_file_abs_path, 'wb') as fp:  # 注意这里一定要先打开文件,然后不断的写入,否则最后的文件大小可能只有4k
        while received_data_size < server_file_size:
            current_received_data_bytes = conn.recv(4096)
            fp.write(current_received_data_bytes)
            received_data_size += len(current_received_data_bytes)

            # show bar
            received_data_percents = int(received_data_size / server_file_size * 100)
            if received_data_percents - received_data_percents_last >2 or received_data_percents == 100:
                my_progress.show_bar(received_data_size, server_file_size)
                received_data_percents_last = received_data_percents

    # start file hash chech
    print('\n')
    local_file_hash = myhash.hash_sha256_with_file(local_file_abs_path)
    print("server file hash : {}, local file hash : {}".format(server_file_hash, local_file_hash))
    if server_file_hash == local_file_hash:
        print("[success]hash check is success")
    else:
        print("[failure]hash check is failure")


def cmd_cd(*args, **kwargs):
    return cmd_basic_execute(*args, **kwargs)


def cmd_mkdir(*args, **kwargs):
    res = cmd_basic_execute(*args, **kwargs)
    res_data_dict = dict(res)
    print(res_data_dict['msg'])


def cmd_rm(*args, **kwargs):
    res = cmd_basic_execute(*args, **kwargs)
    res_data_dict = dict(res)
    print(res_data_dict['msg'])


def cmd_ll(*args, **kwargs):
    res = cmd_basic_execute(*args, **kwargs)
    res_data_dict = dict(res)
    print(res_data_dict['msg'])