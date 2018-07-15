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
       PIR
    P1  P3  P2
    |   |   |
    |   |   |
2   4   6   8   10  12  14  16  18  20  22  24  26  28  30  32  34  36  38  40
1   3   5   7   9   11  13  15  17  19  21  23  25  27  29  31  33  35  37  39
|           |   |
+--------+  |   |
         |  |   |
         P1 P4 P2
          433 MHz
```

## Installation
```
sudo ./install.sh
```

add in /etc/rc.local before the last line (exit 0):
```
/usr/local/bin/pid/pid.py &
```
