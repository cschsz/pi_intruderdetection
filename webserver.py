#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
import configparser
import log
import threading
import time
import base64
import ssl

s_hsvr = None
s_key  = ""
fkt_alarmstate  = None
fkt_armedstate  = None
fkt_armedupdate = None

#----------------------------[readlog]
def readlog():
    log = ""
    try:
        f = open("/var/log/pid.log","r")
    except Exception:
        try:
            f = open("pid.log","r")
        except Exception:
            return "no log found"

    while True:
        rl = f.readline()
        if not rl:
            break;
        line = str(rl)
        log += line.replace('\n', "<br>")

    return log

#----------------------------[generatehtml]
def generatehtml(logflag):
    html  = "<!docstype html>"
    html += "<html lang='de'>"
    html += "<head>"
    html += "<meta charset='UTF-8'>"
    html += "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    html += "<title>PId</title>"
    if logflag == 0:
        html += "<meta http-equiv='refresh' content='5'>"
    html += "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css' integrity='sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm' crossorigin='anonymous'>"
    html += "<link rel='stylesheet' href='https://use.fontawesome.com/releases/v5.1.1/css/all.css' integrity='sha384-O8whS3fhG2OnA5Kas0Y9l3cfpmYjapjI0E4theH4iuMD+pLhbf6JI0jIMfYcK3yZ' crossorigin='anonymous'>"
    #html += "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css' integrity='sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u' crossorigin='anonymous'>"
    html += "</head>"
    html += "<body>"
    html += "<div class='container'>"
    html += "<main>"
    if logflag == 0:
        html += "<h2><i class='fas fa-home'></i> PId</h2>"
        html += "<p>{:s}</p>".format(time.strftime("%d.%m.%Y %H:%M:%S",time.localtime()))
        html += "<hr>"
        html += "<form action='' method='post'>"
        if fkt_armedstate() == 0:
            html += "<button type='submit' class='btn btn-danger btn-lg' name='arm1'>"
            html += "Scharf&nbsp;"
            html += "<i class='fas fa-lock'></i>"
            html += "</button>"
            html += "&nbsp;"
            html += "<button type='submit' class='btn btn-danger btn-lg' name='arm2'>"
            html += "Teilscharf&nbsp;"
            html += "<i class='fas fa-user-lock'></i>"
            html += "</button>"
        else:
            if fkt_alarmstate() == -1:
                html += "<button type='submit' class='btn btn-outline-danger btn-lg' name='disarm'>"
                html += "Alarm zur&uuml;cksetzen&nbsp;"
                html += "<i class='fas fa-exclamation-triangle'></i>"
            else:
                html += "<button type='submit' class='btn btn-success btn-lg' name='disarm'>"
                html += "Unscharf schalten&nbsp;"
                html += "<i class='fas fa-lock-open'></i>"
            html += "</button>"
        html += "</form>"
        html += "<hr>"
        if   fkt_armedstate() == 1:
            html += "<div class='alert alert-danger' role='alert'>Status: scharf <i class='fas fa-lock'></i></div>"
        elif fkt_armedstate() == 2:
            html += "<div class='alert alert-warning' role='alert'>Status: teilscharf <i class='fas fa-user-lock'></i></div>"
        else:
            html += "<div class='alert alert-success' role='alert'>Status: unscharf <i class='fas fa-lock-open'></i></div>"
        html += "<div class='alert alert-success' role='alert'>Haust&uuml;r: abgeschlossen</div>"
        html += "<div class='alert alert-success' role='alert'>Kellert&uuml;r: abgeschlossen</div>"
        html += "<div class='alert alert-success' role='alert'>Gasmelder: OK</div>"
        html += "<hr>"
        html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='log'>Logfile <i class='fas fa-caret-right'></i></button></form>"
    else:
        html += "<h2><i class='fas fa-file'></i> Logfile</h2>"
        html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='main'><i class='fas fa-caret-left'></i> &Uuml;bersicht</button></form>"
        html += "<p><pre>"
        html += readlog()
        html += "</pre></p>"
        html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='main'><i class='fas fa-caret-left'></i> &Uuml;bersicht</button></form>"
    html += "</main>"
    html += "</div>"
    html += "</body>"
    html += "</html>"
    return html

#----------------------------[RequestHandler]
class RequestHandler(BaseHTTPRequestHandler):
    def resp_header(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def resp_auth(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def senddata(self, data):
        self.wfile.write(bytes(data, "utf-8"))

    def resp_page(self, logflag):
        html = generatehtml(logflag)
        self.senddata(html)

    def do_GET2(self):
        self.resp_header()
        if   self.path == "/":
            self.resp_page(0)
        elif self.path == "/log":
            self.resp_page(1)

    def do_GET(self):
        global s_key
        if s_key == "":
            self.do_GET2()
        else:
            if self.headers.get('Authorization') == None:
                self.resp_auth()
                self.senddata("no auth header received")
                pass
            elif self.headers.get('Authorization') == "Basic "+s_key:
                self.do_GET2()
                pass
            else:
                self.resp_auth()
                self.senddata("not authenticated")
                pass

    def do_POST2(self):
        content_length = self.headers.get('content-length')
        length = int(content_length[0]) if content_length else 0
        val = str(self.rfile.read(length))

        self.resp_header()
        if val.find ("log=") != -1:
            self.resp_page(1)
        else:
            if val.find("arm1=") != -1:
                log.info("websvr", "do_POST: {:s} [{:s}]".format(val, self.address_string()))
                fkt_armedupdate(1)
            elif val.find("arm2=") != -1:
                log.info("websvr", "do_POST: {:s} [{:s}]".format(val, self.address_string()))
                fkt_armedupdate(2)
            elif val.find("disarm=") != -1:
                log.info("websvr", "do_POST: {:s} [{:s}]".format(val, self.address_string()))
                fkt_armedupdate(0)
            self.resp_page(0)

    def do_POST(self):
        global s_key
        if s_key == "":
            self.do_POST2()
        else:
            if self.headers.get('Authorization') == None:
                self.resp_auth()
                self.senddata("no auth header received")
                pass
            elif self.headers.get('Authorization') == "Basic "+s_key:
                self.do_POST2()
                pass
            else:
                self.resp_auth()
                self.senddata("not authenticated")
                pass

#----------------------------[serverthread]
def serverthread():
    global s_hsvr
    global s_key

    log.info("websvr", "init")

    # init server
    config = configparser.ConfigParser()
    config.read('/usr/local/etc/pid.ini')
    try:
        user  = config["WEBSERVER"]["USER"]
        pasw  = config["WEBSERVER"]["PASSWORD"]
    except KeyError:
        user  = ""
        pasw  = ""
        log.info("websvr", "pid.ini not filled")

    # authentication
    phrase = user + ":" + pasw
    if len(phrase) > 1:
        s_key = str(base64.b64encode(bytes(phrase, "utf-8")), "utf-8")
    else:
        log.info("websvr", "authentication is disabled")

    # start
    while True:
        try:
            s_hsvr = HTTPServer(("", 4711), RequestHandler)
        except Exception:
            time.sleep(1)

        try:
            f = open("/usr/local/etc/pid.pem","r")
            f.close()
            try:
                s_hsvr.socket = ssl.wrap_socket(s_hsvr.socket, server_side=True, certfile="/usr/local/etc/pid.pem", ssl_version=ssl.PROTOCOL_TLSv1)
                break
            except Exception as e:
                print (str(e))
                s_hsvr.server_close()
                time.sleep(1)
        except Exception:
            log.info("websvr", "https is disabled")
            break

    # running
    log.info("websvr", "started")
    try:
        s_hsvr.serve_forever()
    except KeyboardInterrupt:
        s_hsvr.server_close()
    log.info("websvr", "stop")
    return

#----------------------------[stop]
def stop():
    global s_hsvr
    if s_hsvr != None:
        s_hsvr.shutdown()
    return

#----------------------------[start]
def start(falarmstate, farmedstate, farmedupdate):
    global fkt_alarmstate
    global fkt_armedstate
    global fkt_armedupdate

    fkt_alarmstate = falarmstate
    fkt_armedstate = farmedstate
    fkt_armedupdate = farmedupdate

    thread = threading.Thread(target=serverthread, args=[])
    thread.start()
    return
