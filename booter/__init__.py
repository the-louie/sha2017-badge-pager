# import shell

import network

sta_if = network.WLAN(network.STA_IF);
sta_if.active(True)
a = sta_if.scan()
sta_if.connect("SHA2017-insecure")


#####

import io
import urequests as requests
r = requests.get('https://raw.githubusercontent.com/the-louie/sha2017-badge-pager/master/__init__.py')

f = io.open('/lib/louie-test/__init__.py', 'w')
f.write(r.text)
f.close()


######

import deepsleep
deepsleep.reboot()