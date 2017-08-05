from time import *
import ugfx, gc, wifi, badge, deepsleep, urandom
from umqtt.simple import MQTTClient
import ubinascii
import network
import easyrtc

VERSION = 0.2
MAC = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
CLIENTNAME = "SHAPAGER.{}".format(MAC)
MQTT_PATH = "sha2017pager/swe/{}".format(MAC)

ugfx.init()
#ugfx.LUT_FULL
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
    print "running_leds({})".format(i)
    global led_data
    badge.leds_send_data(led_data, 24)
    led_data = rotate(led_data, (i*4) % 24)

def leds_off():
    print "leds_off()"
    badge.leds_send_data([0]*24, 24)

def messages_acc(pushed):
    print "messages_acc({})".format(pushed)
    if pushed:
        new_message = False
        message_queue = []
        leds_off()

def redraw():
    print "redraw()"
    ugfx.clear(ugfx.WHITE)
    ugfx.flush()
    sleep(0.2)
    ugfx.clear(ugfx.BLACK)
    ugfx.flush()
    sleep(0.2)
    ugfx.clear(ugfx.WHITE)
    ugfx.flush()

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    global new_message
    text = msg.decode('utf-8')
    print("New message: {} > {}".format(topic.decode('utf-8'), text))
    redraw()
    ugfx.string(0,0,"Badgepager v.{} ({})".format(VERSION, MAC),"Roboto_BlackItalic16",ugfx.BLACK)
    ugfx.flush()

    if text.lower() == "reset":
        messages_acc(True)
        return

    new_message = True
    message_queue.append("<{}> {}".format(easyrtc.string(), text))

    for i in range(0, len(message_queue)-1):
        ugfx.string(0,35 + (10*i), message_queue[i], "Roboto_Regular12", ugfx.BLACK)

    ugfx.flush()

def main(server="test.mosquitto.org"):
    global new_message
    print "Running..."

    clientname = 'SHA2017SWE ' + str(urandom.getrandbits(30))
    mqttclient = MQTTClient(clientname, server)
    mqttclient.set_callback(sub_cb)
    mqttclient.connect()
    mqttclient.subscribe(MQTT_PATH)

    mqttclient.check_msg()
    ugfx.string(10,10,"Badgepager online","Roboto_Regular12", 0)
    ugfx.flush()

    i = 0
    while True:
        mqttclient.check_msg()
        print "checked: {}".format(new_message)
        if new_message:
            running_leds(i)
            i += 1

        sleep(1)
    mqttclient.disconnect()

def go_home(pushed):
    print "go_home({})".format(pushed)
    if pushed:
        import machine
        machine.deepsleep(1)

ugfx.input_attach(ugfx.BTN_B, go_home)
ugfx.input_attach(ugfx.BTN_A, messages_acc)

print "test"
main()
