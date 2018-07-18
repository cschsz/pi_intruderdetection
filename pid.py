#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

# own modules
import gpio as GPIO
import webserver
import log

armed = 0

piralarm = False
piracnt  = 0
piralast = time.time()
atoggle = True
stoggle = True
scnt = 0

#----------------------------[alarmstate]
def alarmstate():
    return piralarm

#----------------------------[armedstate]
def armedstate():
    return armed

#----------------------------[armedupdate]
def armedupdate(val):
    global armed
    armed = val
    return

#----------------------------[pir_check]
def pir_check():
    global piralarm
    global piracnt
    global piralast

    if GPIO.pir() == 1:
        piracnt += 1
    else:
        piracnt = 0
        if piralarm == True:
            piralarm = False
            log.info("pir", "reset ({:.0f})".format(time.time() - piralast))

    if piracnt >= 30:
        if piralarm == False:
            piralarm = True
            log.info("pir", "alarm ({:.0f})".format(time.time() - piralast))
            piralast = time.time()
    return

#----------------------------[alarm_check]
def alarm_check():
    global atoggle

    if armedstate():
        if alarmstate():
            if armedstate() == 1:
                GPIO.sirene(1)
            else:
                GPIO.beeper(1)
            atoggle = not atoggle
            GPIO.ledred(atoggle)
        else:
            GPIO.ledred(1)
    else:
        GPIO.beeper(0)
        GPIO.sirene(0)
        GPIO.ledred(0)

#----------------------------[status_led]
def status_led():
    global stoggle
    global scnt

    scnt += 1
    if scnt >= 10:
        scnt = 0
        stoggle = not stoggle
        GPIO.ledgrn(stoggle)

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
