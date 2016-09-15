#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:my_progress.py
@time(UTC+8):16/9/12-17:42
'''
import sys, time


def show_bar(progress, total):
    persent = int(progress/total * 100)
    # count_of_char = int(persent/2)
    sys.stdout.write('\r%d%%' % persent)
    # sys.stdout.write('\r' + '=' * count_of_char + '%d%%' % persent)
    sys.stdout.flush()


if __name__ == '__main__':
    for i in range(10):
        show_bar(i+1, 10)
        time.sleep(1)