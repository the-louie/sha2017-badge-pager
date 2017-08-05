import ugfx, gc, wifi, badge, deepsleep, urandom
from time import *
from umqtt.simple import MQTTClient

VERSION = 0.1

ugfx.init()
ugfx.LUT_FULL
ugfx.input_init()
badge.leds_init()
badge.leds_enable()

# Make sure WiFi is connected
wifi.init()

ugfx.clear(ugfx.WHITE);
ugfx.string(10,10,"Waiting for wifi...","Roboto_Regular12", 0)
ugfx.flush()

# Wait for WiFi connection
while not wifi.sta_if.isconnected():
    sleep(0.2)

ugfx.clear(ugfx.WHITE);
ugfx.string(10,10,"Connecting to MQTT...","Roboto_Regular12", 0)
ugfx.flush()

new_message = False
led_data = bytes([
    64, 0, 0, 128,
    0, 0, 0, 0,
    0, 0, 64, 128,
    0, 0, 0, 0,
    64, 64, 0, 128,
    0, 0, 0, 0,
])

message_queue = []

def rotate(l, n):
    return l[n:] + l[:n]

def running_leds(i):
    global led_data
    badge.leds_send_data(led_data, 24)
    led_data = rotate(led_data, (i*4) % 24)

def leds_off():
    badge.leds_send_data([0]*24, 24)

def messages_acc(pushed):
    if pushed:
        new_message = False
        message_queue = []
        leds_off()

def redraw():
    ugfx.clear(ugfx.WHITE)
    ugfx.flush()
    sleep(0.1)
    ugfx.clear(ugfx.BLACK)
    ugfx.flush()
    sleep(0.1)
    ugfx.clear(ugfx.WHITE)
    ugfx.flush()

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    global new_message
    text = msg.decode('utf-8')

    redraw()
    ugfx.string(0,0,"Badgepager v.{}".format(VERSION),"Roboto_BlackItalic24",ugfx.BLACK)
    ugfx.flush()

    if text.lower() == "reset":
        messages_acc()
        return

    new_message = True

    for i in range(0, len(message_queue)-1):
        ugfx.string(0,25 + (10*i), text, "Roboto_Regular12", ugfx.BLACK)

    ugfx.flush()

def main(server="test.mosquitto.org"):
    global new_message

    clientname = 'SHA2017SWE ' + str(urandom.getrandbits(30))
    c = MQTTClient(clientname, server)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(b"sha2017pager/swe/MA:CK:AD:DR:SS")

    c.check_msg()
    ugfx.string(10,10,"Badgepager online","Roboto_Regular12", 0)
    ugfx.flush()

    i = 0
    while True:
        c.check_msg()
        if new_message:
            running_leds(i)
            i += 1

        sleep(1)
    c.disconnect()

def go_home(pushed):
    if pushed:
        import machine
        machine.deepsleep(1)

ugfx.input_attach(ugfx.BTN_B, go_home)
ugfx.input_attach(ugfx.BTN_A, messages_acc)

main()