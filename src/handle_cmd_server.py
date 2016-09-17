#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:handle_cmd_server.py
@time(UTC+8):16/9/13-13:41
'''

import os, sys, subprocess, re, json
import configparser
from lib import myhash, my_progress, my_subprocess
from config import setting
from lib import get_dir_size

def get_config_file_value(section, key):
    config = configparser.ConfigParser()
    config.read(setting.LIFTP_CONFIG_FILE_PATH, encoding='utf-8')
    if key == "chroot":
        res = config.getboolean(section, key)
    else:
        res = config.get(section, key)
    return res


def cmd_basic_execute(*args, **kwargs):
    recved_data_dict = dict(args[0])
    cmd_list = recved_data_dict.get("cmd_list")
    cmd_str = " ".join(cmd_list)
    wd = recved_data_dict.get("wd")

    conn = args[1]
    logined_user = args[2]

    user_home_dir = get_config_file_value(logined_user, "home")
    user_chroot_flag = get_config_file_value(logined_user, "chroot")

    execute_cmd_flag = False  # start execute_cmd_flag is False default
    ret_data_dict = {}  # {'msg':'', 'wd': ''}

    # 如果是删除,那么命令要重新构造一下  --> rm -rf dirname/filename
    if cmd_list[0] == "rm":
        cmd_list.insert(1, '-rf')
        cmd_str = " ".join(cmd_list)

    # 如果是ll , 重新构造一下cmd
    if cmd_list[0] == "ll":
        cmd_str = "ls -al"

    # 等待客户端返回开始执行命令的信号
    execute_cmd_str = str(conn.recv(1024), encoding='utf-8')
    if execute_cmd_str == 'start execute cmd':
        execute_cmd_flag = True

    # start execute cmd in server
    if not execute_cmd_flag:
        # 不能开始
        res_str = "not received start execute cmd signal"
        print(res_str)
    else:
        # start execute cmd in server
        res_str = str(my_subprocess.execute_cmd(cmd_str, wd), encoding='utf-8')

    # gen return data dict
    ret_data_dict["msg"] = res_str
    ret_data_dict["wd"] = wd  # 其实这里对于mkdir rm 没有用, 先保留吧
    ret_data_json = json.dumps(ret_data_dict)

    # send ret_data_size to client
    ret_data_size = len(ret_data_json)
    conn.send(bytes(str(ret_data_size), encoding='utf-8'))  # int -->str -- > bytes  不要加encoding='utf-8'

    # wait for client ack --- ready for receive data
    start_trans_str = str(conn.recv(1024), encoding='utf-8')
    if start_trans_str == "start trans":
        # send to client
        conn.send(bytes(ret_data_json, encoding='utf-8'))
    else:
        print("client is not ready to recved result")

    return res_str


def get_user_quota_bytes(logined_user):
    user_quota_str = str(get_config_file_value(logined_user, "quota"))
    print("user_quota_in_config:", user_quota_str)
    number, unit, normal_null = re.split('([kKmMgG])', user_quota_str)

    if unit == "m" or unit == "M":
        user_quota_bytes = int(number) * 1000 * 1000
    elif unit == "k" or unit == "K":
        user_quota_bytes = int(number) * 1000
    elif unit == "g" or unit == "G":
        user_quota_bytes = int(number) * 1000 * 1000 * 1000

    return user_quota_bytes


def cmd_put(*args, **kwargs):
    recv_data_dic = args[0]
    conn = args[1]
    logined_user = args[2]
    user_home_dir = get_config_file_value(logined_user, "home")
    user_chroot_flag = get_config_file_value(logined_user, "chroot")
    user_quota_bytes = get_user_quota_bytes(logined_user)



    # 开始处理文件信息
    client_file_name = recv_data_dic["client_file_name"] # 客户端传过来,客户端文件名字
    server_path = recv_data_dic["server_path"]  # 客户端传过来,用户希望上传到的相对位置
    file_size = recv_data_dic["file_size"]  # 客户端传过来, 文件大小
    file_hash = recv_data_dic["file_hash"]  # 客户端传过来, 文件hash
    user_work_dir = recv_data_dic["wd"]
    server_file_abs_path = os.path.join(user_work_dir, server_path, client_file_name)  # 服务器端构造的 文件的绝对路径
    print('server_file_abs_path:{}'.format(server_file_abs_path))


    # 检查服务器端是否存在 该文件, 如果存在,要返回当前文件的大小
    # {"quota":"over quota | bellow quota", "server_file_size":""}
    send_data_quota_fexist = {}
    server_file_exist_flag = False
    if os.path.exists(server_file_abs_path):
        # file is exist , get the size
        server_file_exist_flag = True
        server_file_size_bytes = os.path.getsize(server_file_abs_path)
        send_data_quota_fexist['server_file_size'] = server_file_size_bytes
        print("file is exist, size:{}".format(server_file_size_bytes))
    else:
        send_data_quota_fexist['server_file_size'] = 0
        print("file is not exist")
        pass

    # 检查磁盘配额, 如果磁盘满了,直接return
    request_quota_flag = str(conn.recv(1024), encoding='utf-8')
    if request_quota_flag == "get quota":
        server_dirsize_forecast = get_dir_size.get_dir_size(user_home_dir) + file_size
        print('forecast size: {} bytes, quota: {} bytes'.format(server_dirsize_forecast, user_quota_bytes))

        if server_dirsize_forecast > user_quota_bytes :
            # over quota
            send_data_quota_fexist['quota'] = 'over quota'
            conn.send(bytes(json.dumps(send_data_quota_fexist), encoding='utf-8'))
            return
        else:
            send_data_quota_fexist['quota'] = 'below quota'
            conn.send(bytes(json.dumps(send_data_quota_fexist), encoding='utf-8'))
    else:
        print("client should request quota infomation")

    # gen 刚开始的时候,已经收到的数据和百分比
    if server_file_exist_flag:
        recved_size = server_file_size_bytes
        recved_size_percents_last = int(server_file_size_bytes / file_size * 100)
    else:
        recved_size = 0
        recved_size_percents_last = 0  # 每次加上2个个百分点以上才显示

    # 开始接收文件本身
    if server_file_exist_flag:
        # 服务器端有文件时候的接收数据的方式
        with open(server_file_abs_path, 'ab') as fp:
            print("start recvdata -- recved_size: {}, recved_size_percents_last: {} , file_size: {}".format(
                recved_size,
                recved_size_percents_last,
                file_size,
            ))
            while recved_size < file_size:
                current_recved_data_bytes = conn.recv(4096)
                fp.write(current_recved_data_bytes)
                recved_size += len(current_recved_data_bytes)

                # 显示进度条, 控制显示的粒度为2个点,否则屏幕输出太多,会卡死
                recved_size_percents = int(recved_size / file_size * 100)
                if recved_size_percents - recved_size_percents_last > 2 or recved_size_percents == 100:
                    my_progress.show_bar(recved_size, file_size)
                    recved_size_percents_last = recved_size_percents
                    # print("recved_size:{} file_size:{}".format(recved_size, file_size))
            print("\nrecved success")
    else:
        # 服务器端没有文件的时候的接收数据方式
        with open(server_file_abs_path, 'wb') as fp:
            while recved_size < file_size:
                current_recved_data_bytes = conn.recv(4096)
                fp.write(current_recved_data_bytes)
                recved_size += len(current_recved_data_bytes)

                # 显示进度条, 控制显示的粒度为2个点,否则屏幕输出太多,会卡死
                recved_size_percents = int(recved_size / file_size * 100)
                if recved_size_percents - recved_size_percents_last > 2 or recved_size_percents == 100:
                    my_progress.show_bar(recved_size, file_size)
                    recved_size_percents_last = recved_size_percents
                    # print("recved_size:{} file_size:{}".format(recved_size, file_size))
            print("\nrecved success")



    # start check file sha256(hash)
    server_file_sha256 = myhash.hash_sha256_with_file(server_file_abs_path)
    print("server_file_sha256:{}, client_file_hash:{}".
          format(server_file_sha256, file_hash))
    if server_file_sha256 == file_hash:
        conn.send(bytes("success", encoding='utf-8'))
    else:
        print("[err]file check failure")
        conn.send(bytes("failure", encoding='utf-8'))


def cmd_ls(*args, **kwargs):
    print("start execute cmd_ls")
    recved_data_dict = args[0]
    cmd = recved_data_dict["cmd"]
    work_direction = recved_data_dict["wd"]
    conn = args[1]
    logined_user = args[2]

    # 等待客户端发送开始执行命令的 信号
    execute_cmd_str = str(conn.recv(1024), encoding='utf-8')
    if execute_cmd_str == 'start execute cmd':
        execute_cmd_flag = True
    if execute_cmd_flag:
        res_bytes = my_subprocess.execute_cmd(cmd, work_direction)  # 执行命令得到结果
        conn.send(res_bytes)  # 把结果发送给客户端
    else:
        print("client do not send start execute cmd signal")

    # # 等待客户端的确认消息
    # recved_status_code = int(conn.recv(1024))  # 客户端如果接收成功会返回200
    return True


def cmd_get(*args, **kwargs):
    recved_data_dict = dict(args[0])
    cmd_list = recved_data_dict.get("cmd_list")
    wd = recved_data_dict.get("wd")

    conn = args[1]
    logined_user = args[2]

    server_file_abs_path = os.path.join(wd, cmd_list[1])

    user_home_dir = get_config_file_value(logined_user, "home")
    user_chroot_flag = get_config_file_value(logined_user, "chroot")

    execute_cmd_flag = False  # start execute_cmd_flag is False default


    # 等待客户端返回开始执行命令的信号
    execute_cmd_str = str(conn.recv(1024), encoding='utf-8')
    if execute_cmd_str == 'start execute cmd':
        execute_cmd_flag = True

    # start execute cmd in server
    if not execute_cmd_flag:
        # 不能开始
        res_str = "not received start execute cmd signal"
        print(res_str)
    else:
        # send server file information  to client
        server_file_size = os.stat(server_file_abs_path).st_size
        server_file_hash = myhash.hash_sha256_with_file(server_file_abs_path)
        server_file_info_dict = {"file_hash": server_file_hash, "file_size": server_file_size}
        server_file_info_json = json.dumps(server_file_info_dict)
        conn.send(bytes(server_file_info_json, encoding='utf-8'))  # send server file infomation to client e.g. size hash

        # wait for client ack --- ready for receive data
        start_trans_str = str(conn.recv(1024), encoding='utf-8')
        if start_trans_str == "start trans":
            # send file data bytes stream to client
            with open(server_file_abs_path, 'rb') as fp:
                for line_bytes in fp:
                    conn.send(line_bytes)
        else:
            print("client is not ready to recved result")



def cmd_cd(*args, **kwargs):
    recved_data_dict = dict(args[0])
    cmd_list = recved_data_dict.get("cmd_list")
    wd = recved_data_dict.get("wd")

    conn = args[1]
    logined_user = args[2]

    user_home_dir = get_config_file_value(logined_user, "home")
    user_chroot_flag = get_config_file_value(logined_user, "chroot")

    execute_cmd_flag = False  # start execute_cmd_flag is False default
    ret_data_dict = {}  # {'msg':'', 'wd': ''}


    # 等待客户端返回开始执行命令的信号
    execute_cmd_str = str(conn.recv(1024), encoding='utf-8')
    if execute_cmd_str == 'start execute cmd':
        execute_cmd_flag = True

    # start execute logic of change work directiory
    if execute_cmd_flag:
        if cmd_list[1] == "..":
            # 切换到上级目录
            wd_tmp = os.path.dirname(wd)
            if re.search(user_home_dir, wd_tmp):
                # 还在家目录下面
                wd = wd_tmp
                res_msg = "cwd success: {}".format(wd_tmp)
            else:
                # 需要判断是否有读取该目录的权限
                if user_chroot_flag:
                    wd = wd_tmp
                    res_msg = "cwd success: {}".format(wd_tmp)
                else:
                    res_msg = "you can not access dir: {}".format(wd_tmp)

        else:
            # 切换到下级目录
            wd_tmp = os.path.join(wd, cmd_list[1])

            # check wd_tmp is a direction
            if not os.path.isdir(wd_tmp):
                res_msg = "no such dir: {}".format(wd_tmp)
            else:
                res_msg = "cwd success: {}".format(wd_tmp)
                wd = wd_tmp

        ret_data_dict['msg'] = res_msg
        ret_data_dict['wd'] = wd
        ret_data_json = json.dumps(ret_data_dict)

        # send ret_data_size to client
        ret_data_size = len(ret_data_json)
        conn.send(bytes(str(ret_data_size), encoding='utf-8'))  # int -->str -- > bytes  不要加encoding='utf-8'

        # wait for client ack --- ready for receive data
        start_trans_str = str(conn.recv(1024), encoding='utf-8')
        if start_trans_str == "start trans":
            # send to client
            conn.send(bytes(ret_data_json, encoding='utf-8'))
        else:
            print("client is not ready to recved result")

        # send data to client
        # conn.send(bytes(json.dumps(ret_data_dict), encoding='utf-8'))


def cmd_mkdir(*args, **kwargs):
    cmd_basic_execute(*args, **kwargs)


def cmd_rm(*args, **kwargs):
    cmd_basic_execute(*args, **kwargs)

def cmd_ll(*args, **kwargs):
    cmd_basic_execute(*args, **kwargs)



if __name__ == '__main__':
    # res = my_subprocess.execute_cmd("ls", "/data/yangli.d/")
    # print(res)

    # test get quota units: bytes
    # res = get_user_quota_bytes("yangli")
    # print(res)
    pass

