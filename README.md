# pi_intruderdetection
PIR intruder detection with alarm sound and app control on raspberry pi

Key features of this project are:
* PIR
* Sirene
* 433 MHz
* Android app or web access

Programm logging is found in /var/log/pid.log

## Preparation
```
sudo apt-get update
sudo apt-get install python3-rpi.gpio
```

## Running
```
python3 pid.py
```

If already "installed" execute this before running from console:
```
ps -aux | grep pid.py
sudo kill [pid]
```

## Hardware layout
http://rpi.science.uoit.ca/lab/gpio/
```
                                                                +-<-+
                                                                |   |
       PIR                                                      |  LED
    P1  P3  P2                                                  |  red
    |   |   |                                                   |  1k0
    |   |   |                                                   |   |
5V  5V  GND 8   10  12  GND 16  18  GND 22  24  26  28  GND 32  GND 36  38  40
3V3 3   5   7   GND 11  13  15  3V3 19  21  23  GND 27  29  31  33  35  37  GND
|           |   |   |                                                   |   |
+--------+  |   |   |                                                  1k0  ^
         |  |   |   SIR                                                LED  |
         P1 P4 P2                                                     green ^
          433 MHz                                                       |   |
                                                                        +->-+
```

## Installation
```
sudo ./install.sh
```

add in /etc/rc.local before the last line (exit 0):
```
/usr/local/bin/pid/pid.py &
```
