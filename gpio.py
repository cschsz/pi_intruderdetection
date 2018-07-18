#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

try:
    from RPi.GPIO import *
    imp = True
except ImportError:
    imp = False
    #----------------------------[setmode]
    def setmode(board):
        return

    #----------------------------[BOARD]
    def BOARD():
        return

    #----------------------------[setup]
    def setup(led, state):
        return

    #----------------------------[OUT]
    def OUT():
        return

    #----------------------------[IN]
    def IN():
        return

    #----------------------------[PUD_DOWN]
    def PUD_DOWN():
        return

    #----------------------------[LOW]
    def LOW():
        return 0

    #----------------------------[HIGH]
    def HIGH():
        return 1

    #----------------------------[output]
    def output(led, state):
        return

    #----------------------------[input]
    def input(pin):
        return 0

    #----------------------------[cleanup]
    def cleanup():
        return

pin_pir = 8
pin_sir = 11
pin_red = 36
pin_grn = 37
pin_bee = 11

#----------------------------[sirene]
def sirene(value):
    if value == 1:
        output(pin_sir, HIGH)
    else:
        output(pin_sir, LOW)
    return

#----------------------------[beeper]
def beeper(value):
    if value == 1:
        output(pin_bee, HIGH)
    else:
        output(pin_bee, LOW)
    return

#----------------------------[pir]
def pir():
    if input(pin_pir) == 1:
        return 1
    else:
        return 0

#----------------------------[ledred]
def ledred(value):
    if value == 1:
        output(pin_red, HIGH)
    else:
        output(pin_red, LOW)
    return

#----------------------------[ledgrn]
def ledgrn(value):
    if value == 1:
        output(pin_grn, HIGH)
    else:
        output(pin_grn, LOW)
    return

#----------------------------[init]
def init():
    setmode(BOARD)
    if imp == True:
        setup(pin_pir, IN, pull_up_down=PUD_DOWN)
    setup(pin_sir, OUT)
    setup(pin_red, OUT)
    setup(pin_grn, OUT)
    setup(pin_bee, OUT)

    sirene(0)
    beeper(0)
    ledred(0)
    ledgrn(0)
    return

#----------------------------[]
if __name__=='__main__':
    val = 0
    try:
        init()
        while True:
            print(pir())
            sirene(val)
            if val == 1:
                val = 0
            else:
                val = 1
            time.sleep(1)
    except:
        cleanup()
