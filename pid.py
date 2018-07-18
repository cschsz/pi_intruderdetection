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

#----------------------------[main]
def main():
    # init
    GPIO.init()
    webserver.start(alarmstate, armedstate, armedupdate)

    # running
    toggle = True
    while True:
        pir_check()
        time.sleep(0.1)
        if armedstate():
            if alarmstate():
                if armedstate() == 1:
                    GPIO.sirene(1)
                else:
                    GPIO.beeper(1)
                toggle = not toggle
                GPIO.ledred(toggle)
            else:
                GPIO.ledred(1)
        else:
            GPIO.beeper(0)
            GPIO.sirene(0)
            GPIO.ledred(0)

#----------------------------[]
if __name__=='__main__':
    try:
        log.info("main", "starting")
        main()
    except:
        webserver.stop()
        GPIO.cleanup()
        log.info("main", "exit")
