#!/usr/bin/env python3

import configparser
import http.client
import os
import platform
import socket
import syslog
import urllib
try:
    import ipaddress
except:
    pass

def main():
    if os.getenv('PAM_TYPE') != 'open_session':
        return 0
    syslog.openlog(ident="sshd-notify")
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pushover.ini'))
        apikey = config['pushover.net']['apikey']
        userkey = config['pushover.net']['userkey']
        host = platform.uname().node
        user = os.getenv('PAM_USER')
        rhost = os.getenv('PAM_RHOST')
        service = os.getenv('PAM_SERVICE')
    except Exception as msg:
        syslog.syslog(msg)
        return -1

    for filtered_user in config.get('pushover.net', 'ignore_users', fallback="").split(','):
        if user == filtered_user:
            syslog.syslog("skipping alert: user " + user + " in ignore list")

    # don't push notify for private networks
    try:
        for addr in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'):
            privnet = ipaddress.ip_interface(str(addr)).network
            remotenet = ipaddress.ip_interface(str(rhost + "/32")).network
            if privnet.overlaps(remotenet):
                syslog.syslog("skipping alert: login from private address " + rhost)
                return 0
    except:
        pass

    rname = "unknown"
    try:
        rname = socket.gethostbyaddr(rhost)[0]
    except Exception:
        pass

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
                 urllib.parse.urlencode({
                     "token": apikey,
                     "user": userkey,
                     "title": host,
                     "message": user + " logged in via " + service + \
                         " from " + rname + " (" + rhost + ")",
                 }),
                 {"Content-type": "application/x-www-form-urlencoded"})

    try:
        syslog.syslog("alerting on login from " + rhost)
        conn.getresponse()
    except Exception as msg:
        syslog.syslog(msg)



if __name__ == '__main__':
    main()
