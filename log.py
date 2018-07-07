#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

#----------------------------[info]
def info(module, info):
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": [" + module + "] " + info)
    try:
        f = open("/var/log/pid.log","a")
    except Exception:
        f = open("pid.log","a")
    f.write(time.strftime("%Y-%m-%d %H:%M:%S") + ": [" + module + "] " + info + "\r\n")
    f.close()
    return
