#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
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
fkt_siren       = None
fkt_beeper      = None

FAVICON = b"AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAB\
            ILAAASCwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
            AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjAA\
            AATQAAAE0AAABNAAAAOAAAAAAAAAAAAAAAOAAAAE0AAABNAAAATQAAACMAAAAA\
            AAAAAAAAAAAAAAAAAAAAtAAAAP8AAAD/AAAA/wAAALoAAAAAAAAAAAAAALoAAA\
            D/AAAA/wAAAP8AAAC0AAAAAAAAAAAAAAAAAAAAAAAAALcAAAD/AAAA/wAAAP8A\
            AAC6AAAAAAAAAAAAAAC6AAAA/wAAAP8AAAD/AAAAtwAAAAAAAAAAAAAAAAAAAA\
            AAAAC3AAAA/wAAAP8AAAD/AAAAugAAAAAAAAAAAAAAugAAAP8AAAD/AAAA/wAA\
            ALcAAAAAAAAAAAAAAAAAAAAAAAAAtwAAAP8AAAD/AAAA/wAAANwAAAB/AAAAfw\
            AAANwAAAD/AAAA/wAAAP8AAAC3AAAAAAAAAAAAAAAEAAAAAgAAALcAAAD/AAAA\
            /wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAtwAAAAIAAAAEAA\
            AAsAAAAK8AAABbAAAA8wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/\
            AAAA8wAAAFsAAACvAAAAsAAAAIkAAAD+AAAA0AAAAE8AAADfAAAA/wAAAP8AAA\
            D/AAAA/wAAAP8AAAD/AAAA3wAAAE8AAADQAAAA/gAAAIkAAAAAAAAAXwAAAPgA\
            AADoAAAAUAAAAMIAAAD/AAAA/wAAAP8AAAD/AAAAwgAAAFEAAADoAAAA+AAAAF\
            8AAAAAAAAAAAAAAAAAAAA7AAAA6AAAAPcAAABlAAAAmwAAAP8AAAD/AAAAmwAA\
            AGUAAAD3AAAA/wAAALcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAADRAAAA/g\
            AAAIkAAABwAAAAcAAAAIkAAAD+AAAA/wAAAP8AAAC3AAAAAAAAAAAAAAAAAAAA\
            AAAAAAAAAAAAAAAADQAAAK8AAAD/AAAAsQAAALEAAAD/AAAArgAAANwAAAD/AA\
            AAtwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAhwAAAP4AAAD+\
            AAAAhwAAAAIAAADSAAAA/wAAALcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
            AAAAAAAAAAAAAAAABDAAAAQwAAAAAAAAAAAAAASgAAAGAAAABAAAAAAAAAAAAA\
            AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
            AAAAAAAAAAAAAAAAAAAAAA//8AAMGDAADBgwAAwYMAAMGDAADAAwAAAAAAAAAA\
            AAAAAAAAAAAAAMADAADgAwAA8AMAAPgDAAD8IwAA//8AAA=="

#----------------------------[readlog]
def readlog(logflag):
    if   logflag == 1:
        compare = "event"
    elif logflag == 2:
        compare = "websvr"
    elif logflag == 3:
        compare = "main"
    elif logflag == 4:
        compare = "rf"
    elif logflag == 5:
        compare = "pir"
    else:
        compare = " "

    log = ""
    try:
        f = open("/var/log/pid_{:s}.log".format(time.strftime("%Y-%m")),"r")
    except Exception:
        try:
            f = open("pid_{:s}.log".format(time.strftime("%Y-%m")),"r")
        except Exception:
            return "no log found"

    while True:
        rl = f.readline()
        if not rl:
            break;
        line = str(rl)
        if line.find(compare) != -1:
            log += line.replace('\n', "<br>")

    if log == "":
        log = "nothing to display<br>"

    return log

#----------------------------[generatehtml]
def generatehtml(logflag):
    html  = "<!docstype html>\r\n"
    html += "<html lang='de'>\r\n"
    html += "<head>\r\n"
    html += "<meta charset='UTF-8'>\r\n"
    html += "<meta name='viewport' content='width=device-width, initial-scale=1'>\r\n"
    html += "<title>PId</title>\r\n"
    if logflag == 0:
        html += "<meta http-equiv='refresh' content='10'>\r\n"
    html += "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css' integrity='sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm' crossorigin='anonymous'>\r\n"
    html += "<link rel='stylesheet' href='https://use.fontawesome.com/releases/v5.1.1/css/all.css' integrity='sha384-O8whS3fhG2OnA5Kas0Y9l3cfpmYjapjI0E4theH4iuMD+pLhbf6JI0jIMfYcK3yZ' crossorigin='anonymous'>\r\n"
    html += "</head>\r\n"
    html += "<body>\r\n"
    html += "<div class='container'>\r\n"
    html += "<main>\r\n"
    if logflag == 0:
        html += "<h2><i class='fas fa-home'></i> PId</h2>"
        html += "<p>{:s}</p>".format(time.strftime("%d.%m.%Y %H:%M:%S",time.localtime()))
        html += "<hr>"
        if   fkt_armedstate() == 1:
            html += "Status: scharf <i class='fas fa-lock'></i>"
        elif fkt_armedstate() == 2:
            html += "Status: teilscharf <i class='fas fa-user-lock'></i>"
        else:
            html += "Status: unscharf <i class='fas fa-lock-open'></i>"
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
        html += "Sensoren<br>"
        html += "<div class='alert alert-warning' role='alert'>Haust&uuml;r: ?</div>"
        html += "<div class='alert alert-warning' role='alert'>Kellert&uuml;r: ?</div>"
        html += "<div class='alert alert-warning' role='alert'>Klingel: ?</div>"
        html += "<div class='alert alert-warning' role='alert'>Gasmelder: ?</div>"
        html += "<hr>"
        html += "Protokolldateien<br>"
        html += "<form action='' method='post'>"
        html += "<div class='btn-group' role='group' aria-label='Basic example'>"
        html += "<button type='submit' class='btn btn-primary' name='log1'>EVT</button>"
        html += "<button type='submit' class='btn btn-outline-primary' name='log2'>WEB</button>"
        html += "<button type='submit' class='btn btn-primary' name='log3'>PRG</button>"
        html += "<button type='submit' class='btn btn-outline-primary' name='log4'>433</button>"
        html += "<button type='submit' class='btn btn-primary' name='log5'>PIR</button>"
        html += "<button type='submit' class='btn btn-outline-primary' name='log6'>ALL</button>"
        html += "</div>"
        html += "</form>"
        html += "<hr>"
        html += "Funktionstests<br>"
        html += "<form action='' method='post'>"
        html += "<div class='btn-group' role='group' aria-label='Basic example'>"
        html += "<button type='submit' class='btn btn-secondary' name='test1'>Sirene</button>"
        html += "<button type='submit' class='btn btn-outline-secondary' name='test2'>Beeper</button>"
        html += "</div>"
        html += "</form>"
    elif logflag:
        html += "<h2><i class='fas fa-file'></i> Protokolldatei</h2>"
        html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='mpage'><i class='fas fa-caret-left'></i> &Uuml;bersicht</button></form>"
        html += "<p><pre>"
        html += readlog(logflag)
        html += "</pre></p>"
        html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='mpage'><i class='fas fa-caret-left'></i> &Uuml;bersicht</button></form>"
    html += "\r\n</main>\r\n"
    html += "</div>\r\n"
    html += "</body>\r\n"
    html += "</html>\r\n"
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

    def resp_location(self, path):
        self.send_response(302)
        self.send_header('Location', path)
        self.end_headers()

    def senddata(self, data):
        try:
            self.wfile.write(bytes(data, "utf-8"))
        except Exception as e:
            log.info("websvr", "exception! (senddata) {:s} [{:s}]".format(str(e), self.address_string()))

    def resp_page(self, logflag):
        html = generatehtml(logflag)
        self.senddata(html)

    def do_GET2(self):
        if self.path == "/favicon.ico":
            self.send_response(200)
            self.send_header('Content-type', 'image/gif')
            self.end_headers()
            self.wfile.write(base64.b64decode(FAVICON))
        else:
            self.resp_header()
            path = str(self.path)
            if path[:4] == "/log" and len(path) >= 5:
                self.resp_page(int(path[4]))
            else:
                self.resp_page(0)

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

        pos = val.find("log")
        if   pos != -1:
            if pos + 4 < len(val):
                log.info("websvr", "get {:s} [{:s}]".format(val, self.address_string()))
                self.resp_location(val[pos:pos+4])
                return
        elif val.find("arm1=") != -1:
            log.info("event", "armed [{:s}]".format(self.address_string()))
            fkt_armedupdate(1)
        elif val.find("arm2=") != -1:
            log.info("event", "armed2 [{:s}]".format(self.address_string()))
            fkt_armedupdate(2)
        elif val.find("disarm=") != -1:
            log.info("event", "disarmed [{:s}]".format(self.address_string()))
            fkt_armedupdate(0)
        elif val.find("test1=") != -1:
            log.info("event", "test siren [{:s}]".format(self.address_string()))
            fkt_siren(1)
            time.sleep(1)
            fkt_siren(0)
        elif val.find("test2=") != -1:
            log.info("event", "test beeper [{:s}]".format(self.address_string()))
            fkt_beeper(1)
            time.sleep(1)
            fkt_beeper(0)
        self.resp_location("/")

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
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """

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
            s_hsvr = ThreadedHTTPServer(("", 4711), RequestHandler)
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
def start(falarmstate, farmedstate, farmedupdate, fktsiren, fktbeeper):
    global fkt_alarmstate
    global fkt_armedstate
    global fkt_armedupdate
    global fkt_siren
    global fkt_beeper

    fkt_alarmstate  = falarmstate
    fkt_armedstate  = farmedstate
    fkt_armedupdate = farmedupdate
    fkt_siren       = fktsiren
    fkt_beeper      = fktbeeper

    thread = threading.Thread(target=serverthread, args=[])
    thread.start()
    return
