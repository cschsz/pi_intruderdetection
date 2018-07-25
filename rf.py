#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import signal
import time
import log

try:
    from rpi_rf import RFDevice
    imp = True
except ImportError:
    imp = False

sflag = False
fkt_codeupdate = None

#----------------------------[rfthread]
def rfthread():
    lastcode = ""

    if imp == True:
        log.info("rf", "init")
        rfdevice = RFDevice(13)
        rfdevice.enable_rx()
        timestamp = None
        log.info("rf", "started")
        while sflag == False:
            if rfdevice.rx_code_timestamp != timestamp:
                timestamp = rfdevice.rx_code_timestamp
                log.info("rf", str(rfdevice.rx_code))
                if lastcode != str(rfdevice.rx_code):
                    lastcode = str(rfdevice.rx_code)
                else:
                    fkt_codeupdate(str(rfdevice.rx_code))
            time.sleep(0.01)
        rfdevice.cleanup()
        log.info("rf", "stop")
    else:
        log.info("rf", "debug")
        while sflag == False:
            time.sleep(0.01)
        log.info("rf", "stop")

    return

#----------------------------[stop]
def stop():
    global sflag
    sflag = True
    return

#----------------------------[start]
def start(fcodeupdate):
    global fkt_codeupdate

    fkt_codeupdate = fcodeupdate
    thread = threading.Thread(target=rfthread, args=[])
    thread.start()
    return
