#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

# own modules
import gpio as GPIO
import webserver
import log
import mail
import rf

s_armed = 0

s_galarm = False
t_ga = time.time()
s_needrst = False
s_pirdetection = False
s_pircnt  = 0
t_pirlast = time.time()
s_atoggle = True
s_stoggle = True
s_scnt = 0
s_rfcode = ""
s_rflcode = ""
s_dobeep = 0
s_teststate = 0

#----------------------------[alarmstate]
def teststate(val):
    global s_teststate
    s_teststate = val

#----------------------------[alarmstate]
def alarmstate():
    if   s_needrst:
        return -1
    elif s_pirdetection:
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

#----------------------------[rfupdate]
def rfupdate(code):
    global s_rfcode
    global s_rflcode
    global s_dobeep

    s_rfcode = code
    if s_rflcode != s_rfcode:
        s_rflcode = s_rfcode
        if   s_rfcode == "86356" or s_rfcode == "87124" or s_rfcode == "87364" or s_rfcode == "87316":
            log.info("event", "armed by " + code)
            armedupdate(2)
            s_dobeep = 1
        elif s_rfcode == "86353" or s_rfcode == "87121" or s_rfcode == "87361" or s_rfcode == "87313":
            log.info("event", "disarmed by " + code)
            armedupdate(0)
            s_dobeep = 2
    return

#----------------------------[pir_check]
def pir_check():
    global s_pirdetection
    global s_pircnt
    global t_pirlast

    if GPIO.pir() == 1:
        s_pircnt += 1
    else:
        s_pircnt = 0
        if s_pirdetection == True:
            s_pirdetection = False
            if armedstate():
                log.info("event", "pir reset ({:.0f})".format(time.time() - t_pirlast))
            else:
                log.info("pir", "pir reset ({:.0f})".format(time.time() - t_pirlast))

    if s_pircnt >= 45:
        if s_pirdetection == False:
            s_pirdetection = True
            if armedstate():
                log.info("event", "pir alarm ({:.0f})".format(time.time() - t_pirlast))
            else:
                log.info("pir", "pir alarm ({:.0f})".format(time.time() - t_pirlast))
            t_pirlast = time.time()
    return

#----------------------------[alarm_check]
def alarm_check():
    global s_atoggle
    global s_needrst
    global s_dobeep
    global s_teststate

    if s_teststate == 1:
        s_teststate = 0
        GPIO.siren(1)
        time.sleep(5)
        GPIO.siren(0)

    if s_teststate == 2:
        s_teststate = 0
        GPIO.beeper(1)
        time.sleep(5)
        GPIO.beeper(0)

    if s_dobeep == 1:
        s_dobeep = 0
        GPIO.beeper(1)
        time.sleep(0.5)
        GPIO.beeper(0)

    if s_dobeep == 2:
        s_dobeep = 0
        GPIO.beeper(1)
        time.sleep(0.5)
        GPIO.beeper(0)
        time.sleep(0.5)
        GPIO.beeper(1)
        time.sleep(0.5)
        GPIO.beeper(0)

    if armedstate():
        if s_pirdetection == True:
            if armedstate() == 1:
                GPIO.siren(1)
            else:
                GPIO.beeper(1)
            s_atoggle = not s_atoggle
            GPIO.ledred(s_atoggle)
            if s_needrst == False:
                s_needrst = True
                mail.send("ALARM", "PIR ALARM")
        else:
            GPIO.ledred(1)
    else:
        GPIO.beeper(0)
        GPIO.siren(0)
        GPIO.ledred(0)
        s_needrst = False

#----------------------------[status_led]
def status_led():
    global s_stoggle
    global s_scnt

    if s_pirdetection == True:
        val = 2
    else:
        val = 10

    s_scnt += 1
    if s_scnt >= val:
        s_scnt = 0
        s_stoggle = not s_stoggle
        GPIO.ledgrn(s_stoggle)

#----------------------------[main]
def main():
    # init
    GPIO.init()
    rf.start(rfupdate)
    webserver.start(alarmstate, armedstate, armedupdate, teststate)

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
        mail.send("info", "Restarted")
        main()
    except:
        webserver.stop()
        rf.stop()
        time.sleep(0.5)
        GPIO.cleanup()
        log.info("main", "exit")
