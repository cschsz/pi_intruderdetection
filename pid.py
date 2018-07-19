#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

# own modules
import gpio as GPIO
import webserver
import log

s_armed = 0

s_galarm = False
t_ga = time.time()
s_needrst = False
s_piralarm = False
s_pircnt  = 0
t_pirlast = time.time()
s_atoggle = True
s_stoggle = True
s_scnt = 0

#----------------------------[alarmstate]
def alarmstate():
    if   s_needrst:
        return -1
    elif s_piralarm:
        return 1
    else:
        return 0

#----------------------------[armedstate]
def armedstate():
    return s_armed

#----------------------------[armedupdate]
def armedupdate(val):
    global s_armed
    s_armed = val
    return

#----------------------------[pir_check]
def pir_check():
    global s_piralarm
    global s_pircnt
    global t_pirlast

    if GPIO.pir() == 1:
        s_pircnt += 1
    else:
        s_pircnt = 0
        if s_piralarm == True:
            s_piralarm = False
            log.info("event", "pir reset ({:.0f})".format(time.time() - t_pirlast))

    if s_pircnt >= 30:
        if s_piralarm == False:
            s_piralarm = True
            log.info("event", "pir alarm ({:.0f})".format(time.time() - t_pirlast))
            t_pirlast = time.time()
    return

#----------------------------[alarm_check]
def alarm_check():
    global s_atoggle
    global s_needrst

    if armedstate():
        if s_piralarm == True:
            if armedstate() == 1:
                GPIO.sirene(1)
            else:
                GPIO.beeper(1)
            s_atoggle = not s_atoggle
            GPIO.ledred(s_atoggle)
            s_needrst = True
        else:
            GPIO.ledred(1)
    else:
        GPIO.beeper(0)
        GPIO.sirene(0)
        GPIO.ledred(0)

#----------------------------[status_led]
def status_led():
    global s_stoggle
    global s_scnt

    s_scnt += 1
    if s_scnt >= 10:
        s_scnt = 0
        s_stoggle = not s_stoggle
        GPIO.ledgrn(s_stoggle)

#----------------------------[main]
def main():
    # init
    GPIO.init()
    webserver.start(alarmstate, armedstate, armedupdate)

    # running
    while True:
        time.sleep(0.1)
        pir_check()
        alarm_check()
        status_led()

#----------------------------[]
if __name__=='__main__':
    try:
        log.info("main", "starting")
        main()
    except:
        webserver.stop()
        GPIO.cleanup()
        log.info("main", "exit")
