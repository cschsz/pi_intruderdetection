#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
import configparser
import log
import threading
import time
import base64
import ssl

hsvr = None
fkt_alarmstate = None
fkt_armedstate = None
fkt_armedupdate = None
key = ""

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

#----------------------------[MyServer]
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
        self.senddata("<!docstype html>")
        self.senddata("<html lang='de'>")
        self.senddata("<head>")
        self.senddata("<meta charset='UTF-8'>")
        self.senddata("<meta name='viewport' content='width=device-width, initial-scale=1'>")
        self.senddata("<title>PId</title>")
        if logflag == 0:
            self.senddata("<meta http-equiv='refresh' content='5'>")
        #self.senddata("<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css' integrity='sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm' crossorigin='anonymous'>")
        self.senddata("<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css' integrity='sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u' crossorigin='anonymous'>")
        self.senddata("</head>")
        self.senddata("<body>")
        self.senddata("<div class='container'>")
        self.senddata("<main>")
        if logflag == 0:
            self.senddata("<h2><span class='glyphicon glyphicon-home' aria-hidden='true'></span> PId</h2>")
            self.senddata("<p>{:s}</p>".format(time.strftime("%d.%m.%Y %H:%M:%S",time.localtime())))
            self.senddata("<hr>")
            if fkt_armedstate() == 0:
                self.senddata("<form action='' method='post'><button type='submit' class='btn btn-danger btn-lg' name='arm1'>Scharf <span class='glyphicon glyphicon-lock' aria-hidden='true'></span></button> <button type='submit' class='btn btn-danger btn-lg' name='arm2'>Teilscharf <span class='glyphicon glyphicon-bed' aria-hidden='true'></span></button></form>")
            else:
                self.senddata("<form action='' method='post'><button type='submit' class='btn btn-success btn-lg' name='disarm'>Unscharf schalten <span class='glyphicon glyphicon-user' aria-hidden='true'></span></button></form>")
            self.senddata("<hr>")
            if   fkt_armedstate() == 1:
                self.senddata("<div class='alert alert-danger' role='alert'>Status: scharf</div>")
            elif fkt_armedstate() == 2:
                self.senddata("<div class='alert alert-warning' role='alert'>Status: teilscharf</div>")
            else:
                self.senddata("<div class='alert alert-success' role='alert'>Status: unscharf</div>")
            self.senddata("<div class='alert alert-success' role='alert'>Haust&uuml;r: abgeschlossen</div>")
            self.senddata("<div class='alert alert-success' role='alert'>Kellert&uuml;r: abgeschlossen</div>")
            self.senddata("<div class='alert alert-success' role='alert'>Gasmelder: OK</div>")
            self.senddata("<hr>")
            self.senddata("<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='log'>Logfile<span class='glyphicon glyphicon-triangle-right' aria-hidden='true'></span></button></form>")
        else:
            self.senddata("<h2><span class='glyphicon glyphicon-file' aria-hidden='true'></span> Logfile</h2>")
            self.senddata("<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='main'><span class='glyphicon glyphicon-triangle-left' aria-hidden='true'></span>&Uuml;bersicht</button></form>")
            self.senddata("<p><pre>")
            self.senddata(readlog())
            self.senddata("</pre></p>")
            self.senddata("<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='main'><span class='glyphicon glyphicon-triangle-left' aria-hidden='true'></span>&Uuml;bersicht</button></form>")
        self.senddata("</main>")
        self.senddata("</div>")
        self.senddata("</body>")
        self.senddata("</html>")

    def do_GET2(self):
        self.resp_header()
        if   self.path == "/":
            self.resp_page(0)
        elif self.path == "/log":
            self.resp_page(1)

    def do_GET(self):
        global key
        if key == "":
            self.do_GET2()
        else:
            if self.headers.get('Authorization') == None:
                self.resp_auth()
                self.senddata("no auth header received")
                pass
            elif self.headers.get('Authorization') == "Basic "+key:
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
                fkt_armedupdate(1)
            elif val.find("arm2=") != -1:
                fkt_armedupdate(2)
            elif val.find("disarm=") != -1:
                fkt_armedupdate(0)
            log.info("websvr", "do_POST: {:s} [{:s}]".format(val, self.address_string()))
            self.resp_page(0)

    def do_POST(self):
        global key
        if key == "":
            self.do_POST2()
        else:
            if self.headers.get('Authorization') == None:
                self.resp_auth()
                self.senddata("no auth header received")
                pass
            elif self.headers.get('Authorization') == "Basic "+key:
                self.do_POST2()
                pass
            else:
                self.resp_auth()
                self.senddata("not authenticated")
                pass

#----------------------------[serverthread]
def serverthread():
    global hsvr
    global key

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
        key = str(base64.b64encode(bytes(phrase, "utf-8")), "utf-8")
    else:
        log.info("websvr", "authentication is disabled")

    # start
    while True:
        try:
            hsvr = HTTPServer(("", 4711), RequestHandler)
        except Exception:
            time.sleep(1)

        try:
            f = open("/usr/local/etc/pid.pem","r")
            f.close()
            try:
                hsvr.socket = ssl.wrap_socket(hsvr.socket, server_side=True, certfile="/usr/local/etc/pid.pem", ssl_version=ssl.PROTOCOL_TLSv1)
                break
            except Exception as e:
                print (str(e))
                hsvr.server_close()
                time.sleep(1)
        except Exception:
            log.info("websvr", "https is disabled")
            break

    # running
    log.info("websvr", "started")
    try:
        hsvr.serve_forever()
    except KeyboardInterrupt:
        hsvr.server_close()
    log.info("websvr", "stop")
    return

#----------------------------[stop]
def stop():
    global hsvr
    if hsvr != None:
        hsvr.shutdown()
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
