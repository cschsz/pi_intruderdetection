#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

# own modules
import gpio as GPIO
import log

acnt  = 0
alarm = False
alast = time.time()

#----------------------------[pir_check]
def pir_check():
    global alarm
    global acnt
    global alast

    if GPIO.pir() == 1:
        acnt += 1
    else:
        acnt = 0
        if alarm == True:
            alarm = False
            log.info("pir", "reset ")
            GPIO.sirene(0)

    if acnt >= 10:
        if alarm == False:
            alarm = True
            log.info("pir", "alarm ({:.0f})".format(time.time() - alast))
            alast = time.time()
        GPIO.sirene(1)
    return

#----------------------------[main]
def main():
    # init
    GPIO.init()

    # running
    while True:
        pir_check()
        time.sleep(0.1)

#----------------------------[]
if __name__=='__main__':
    try:
        log.info("main", "starting")
        main()
    except:
        GPIO.cleanup()
        log.info("main", "exit")
