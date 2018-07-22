#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import log
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#----------------------------[send]
def send(subject, htmlbody):
    # read config
    config = configparser.ConfigParser()
    config.read('/usr/local/etc/pid.ini')
    try:
        host  = config["EMAIL"]["SMPT_HOST"]
        port  = config["EMAIL"]["SMPT_PORT"]
        email = config["EMAIL"]["SMPT_EMAIL"]
        passw = config["EMAIL"]["SMPT_PASSWORD"]
        dest  = config["EMAIL"]["DESTINATION_EMAIL"]
    except KeyError:
        log.info("main", "pid.ini not filled")
        return

    # email login
    try:
        s = smtplib.SMTP(host, port)
        s.starttls()
        s.login(email, passw)
    except Exception as e:
        log.info("main", "SMTP error: " + str(e))
        return

    # prepare email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "PId! {:s}!".format(subject)
    msg['From'] = email
    msg['To'] = dest

    html = """
    <head></head>
    <body>
        %s
    </body>
    """ % htmlbody
    msg.attach(MIMEText(html, 'html'))

    # send email
    try:
        s.sendmail(email, dest, msg.as_string())
        s.quit()
        log.info("main", "email send")
    except Exception as e:
        log.info("main", "SMTP error:" + str(e))

    return
