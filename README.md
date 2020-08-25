a simple notifier, using [pushover](https//pushover.net)

to configure, add a line similar to the following at the 
bottom of /etc/pam.d/sshd

session optional pam_exec.so seteuid /etc/ssh/sshd_notify.py

and create a config file in the same directory

    $ cat /etc/ssh/pushover.ini
    [pushover.net]
    userkey = <KEY>
    apikey = <KEY>
    ignore_users = <list,of,users,to,ignore>
