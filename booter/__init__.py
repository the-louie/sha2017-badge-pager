import shell
import urequests as requests
import io, os
import network

sta_if = network.WLAN(network.STA_IF);
sta_if.active(True)
sta_if.scan()
sta_if.connect("SHA2017-insecure")

r = requests.get('https://github.com/the-louie/sha2017-badge-pager/blob/master/__init__.py')

if not os.path.isdir('lib/louie-test'):
    os.mkdir('/lib/louie-test')

f = io.open('/lib/louie-test/__init__.py', 'w')
f.write(r.text)
f.close()

import deepsleep
deepsleep.reboot()