import shell


import network
sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
sta_if.scan()
sta_if.connect("SHA2017-insecure")

import urequests as requests
r = requests.get('https://louie.se/dumpster/code/sha2017/__init__.py')

import io
f = io.open('/lib/mash-test/__init__.py', 'w')
f.write(r.text)
f.close()

import deepsleep
deepsleep.reboot()