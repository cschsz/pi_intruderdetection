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

#----------------------------[sirene]
def sirene(value):
    if value == 1:
        output(pin_sir, HIGH)
    else:
        output(pin_sir, LOW)
    return

#----------------------------[pir]
def pir():
    if input(pin_pir) == 1:
        return 1
    else:
        return 0

#----------------------------[init]
def init():
    setmode(BOARD)
    if imp == True:
        setup(pin_pir, IN, pull_up_down=PUD_DOWN)
    setup(pin_sir, OUT)

    sirene(0)
    return
