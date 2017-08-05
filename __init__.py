from time import *
import ugfx, gc, wifi, badge, deepsleep, urandom
from umqtt.simple import MQTTClient
import ubinascii
import network
import easyrtc
import sys

print("START")

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
ugfx.string(10,10,"Connecting to MQTT {}...".format(MAC),"Roboto_Regular12", 0)
ugfx.flush()

new_message = False
led_data = bytes([
    8, 0, 0, 0,
    0, 8, 0, 0,
    0, 0, 0, 0,
    0, 0, 8, 0,
    8, 8, 0, 0,
    0, 0, 0, 0,
])

message_queue = []
ack_state = False

def rotate(l, n):
    return l[n:] + l[:n]

def running_leds(i):
    #print("running_leds({})".format(i))
    global led_data
    badge.leds_send_data(led_data, 24)
    led_data = rotate(led_data, (i*4) % 24)

def leds_off():
    #print("leds_off()")
    badge.leds_send_data(bytes([0]*24), 24)

def display_acknack():
    print("display_acknack()")
    ugfx.string(10, 70, "(A) ack", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()
    ugfx.string(10, 80, "(B) nack", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()
    ugfx.string(10, 90, "(START) discard", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()

def clear_msg():
    global new_message
    global message_queue
    global ack_state
    print("clear_msg()")
    new_message = False
    message_queue = []
    leds_off()
    ack_state = False
    redraw()

def btn_a(pushed):
    global ack_state
    print("btn_a({}) ack_state: {}".format(pushed, ack_state))
    if not pushed:
        return

    if not ack_state: # display options to ack || nack
        display_acknack()
        ack_state = True
    elif ack_state:
        clear_msg()
        print("SEND ACK!")
        # TODO: send ACK!

def btn_b(pushed):
    print("btn_b({})".format(pushed))
    global ack_state
    if not pushed or not ack_state:
        return

    clear_msg()
    print("SEND NACK!")
    # TODO: SEND NACK!

def btn_start(pushed):
    print("btn_b({})".format(pushed))
    global ack_state
    if not pushed or not ack_state:
        return

    print("DISCARD!")
    clear_msg()

def redraw():
    #print("redraw()")
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
    global message_queue
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

    for i in range(0, min(9, len(message_queue))):
        print("display: {}, {}: {}".format(0, 35+(10*i), message_queue[i]))
        ugfx.string(0, 35 + (10*i), message_queue[i], "Roboto_Regular12", ugfx.BLACK)
        ugfx.flush()


def main(server="test.mosquitto.org"):
    global new_message
    #print("Running...")

    mqttclient = MQTTClient(CLIENTNAME, server)
    mqttclient.set_callback(sub_cb)
    mqttclient.connect()
    mqttclient.subscribe(MQTT_PATH)

    redraw()

    mqttclient.check_msg()
    ugfx.string(10,10,"Badgepager ({})".format(MAC),"Roboto_Regular12", 0)
    ugfx.flush()

    i = 0
    while True:
        mqttclient.check_msg()
        print("post check_msg(): {}".format(new_message))
        while new_message:
            running_leds(i)
            i += 1
            sleep(0.1)

        sleep(5)

    mqttclient.disconnect()

def btn_select(pushed):
    #print("go_home({})".format(pushed))
    if pushed:
        import machine
        machine.deepsleep(1)

"""
        ugfx.input_attach(ugfx.JOY_UP,lambda pressed: self.btn_up(pressed))
        ugfx.input_attach(ugfx.JOY_DOWN,lambda pressed: self.btn_down(pressed))
        ugfx.input_attach(ugfx.JOY_LEFT,lambda pressed: self.btn_left(pressed))
        ugfx.input_attach(ugfx.JOY_RIGHT,lambda pressed: self.btn_right(pressed))
        ugfx.input_attach(ugfx.BTN_SELECT,lambda pressed: self.btn_select(pressed))
        ugfx.input_attach(ugfx.BTN_START,lambda pressed: self.btn_start(pressed))
        ugfx.input_attach(ugfx.BTN_A,lambda pressed: self.btn_a(pressed))
        ugfx.input_attach(ugfx.BTN_B,lambda pressed: self.btn_b(pressed))
"""

ugfx.input_attach(ugfx.BTN_SELECT, btn_select)
ugfx.input_attach(ugfx.BTN_A, btn_a)
ugfx.input_attach(ugfx.BTN_B, btn_b)
ugfx.input_attach(ugfx.BTN_START, btn_start)

#print("test")
main()
