#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# own modules
import gpio as GPIO
import time
import log

#----------------------------[main]
def main():
    # init
    GPIO.init()

    # running
    last = time.time()
    cnt = 0
    alarm = 0
    while True:
        val = GPIO.pir()
        if val == 1:
            cnt += 1
        else:
            cnt = 0
            if alarm == 1:
                alarm = 0
                log.info("pir", "reset ")
                GPIO.sirene(0)


        if cnt >= 10:
            if alarm == 0:
                alarm = 1
                log.info("pir", "alarm ({:.0f})".format(time.time() - last))
                last = time.time()
            GPIO.sirene(1)

        time.sleep(0.1)

#----------------------------[]
if __name__=='__main__':
    try:
        log.info("main", "starting")
        main()
    except:
        GPIO.cleanup()
        log.info("main", "exit")
