"""
    recieve pages via mqtt
"""
import gc
import json
from time import sleep as sleep

import ugfx
import wifi
import badge
import deepsleep
from umqtt.simple import MQTTClient
import ubinascii
import network
import easyrtc

print("START")

VERSION = 0.2
MAC = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
CLIENTNAME = "SHAPAGER.{}".format(MAC)
MQTT_PATH = "sha2017pager/swe/{}".format(MAC)
MQTT_REPLY_PATH = "sha2017pager/swe/replies"


def rotate(arr, length):
    return arr[length:] + arr[:length]

def running_leds(i):
    print("running_leds({})".format(i))
    global LED_DATA
    badge.leds_send_data(rotate(LED_DATA, (i*i*4) % 24), 24)

def leds_off():
    print("leds_off()")
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
    global ack_state
    print("clear_msg()")
    new_message = False
    leds_off()
    ack_state = False
    clear_screen()

def btn_a(pushed):
    global ack_state
    global mqttclient
    print("btn_a({}) ack_state: {}".format(pushed, ack_state))
    if not pushed:
        return

    if not ack_state: # display options to ack || nack
        display_acknack()
        ack_state = True
    elif ack_state:
        clear_msg()
        print("SEND ACK!")
        mqttclient.publish(MQTT_REPLY_PATH, b"ack")

def btn_b(pushed):
    print("btn_b({})".format(pushed))
    global ack_state
    if not pushed or not ack_state:
        return

    clear_msg()
    print("SEND NACK!")
    mqttclient.publish(MQTT_REPLY_PATH, b"nack")

def btn_start(pushed):
    print("btn_b({})".format(pushed))
    global ack_state
    if not pushed or not ack_state:
        return

    print("DISCARD!")
    clear_msg()

def clear_screen():
    print("clear_screen()")
    ugfx.clear(ugfx.WHITE)
    ugfx.flush()
    #sleep(0.2)
    ugfx.clear(ugfx.BLACK)
    ugfx.flush()
    #sleep(0.2)
    ugfx.clear(ugfx.WHITE)
    ugfx.flush()

def print_std_msg():
    clear_screen()
    ugfx.string(0, 0, "Badgepager v.{} ({})".format(VERSION, MAC), "Roboto_BlackItalic16", ugfx.BLACK)
    ugfx.string(0, 130, "(SELECT) to quit", "Roboto_BlackItalic16", ugfx.BLACK)
    ugfx.flush()

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    global new_message
    data = {}
    try:
        data = json.loads(msg.decode('utf-8'))
    except Exception:
        print("Invalid message: {}".format(msg.decode('utf-8')))
        return

    print("New message: {} > {}".format(topic.decode('utf-8'), data["text"]))
    print_std_msg()

    new_message = True

    print("display: {}, {}: {}".format(0, 45, data.get("text", "")))
    ugfx.string(10, 40, "{} <{}> {}".format(easyrtc.string(), data["sender"], data["text"]), "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(0, 60, "PRESS (A) to contiue", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()


def main():
    global new_message
    global mqttclient
    print("Running...")


    print_std_msg()

    i = 0
    while True:
        mqttclient.check_msg()
        print("post check_msg(): {}".format(new_message))
        if new_message:
            while new_message:
                running_leds(i)
                i += 1
                sleep(0.1)
            print_std_msg()


        sleep(5)

    mqttclient.disconnect()

def btn_select(pushed):
    print("go_home({})".format(pushed))
    if pushed:
        import machine
        machine.deepsleep(1)

print("ugfx init")
ugfx.init()
#ugfx.LUT_FULL
ugfx.input_init()

print("badge init")
badge.leds_init()
badge.leds_enable()

# Make sure WiFi is connected
print("wifi init")
wifi.init()

ugfx.clear(ugfx.WHITE)
ugfx.string(10, 10, "Waiting for wifi...", "Roboto_Regular12", 0)
ugfx.flush()

# Wait for WiFi connection
while not wifi.sta_if.isconnected():
    print("Not connected, waiting...")
    sleep(0.2)

ugfx.clear(ugfx.WHITE)
ugfx.string(10, 10, "Connecting to MQTT {}...".format(MAC), "Roboto_Regular12", 0)
ugfx.flush()

print("mqtt connect...")
mqttclient = MQTTClient(CLIENTNAME, "test.mosquitto.org")
mqttclient.set_callback(sub_cb)
mqttclient.connect()
mqttclient.subscribe(MQTT_PATH)


new_message = False
LED_DATA = bytes([
    8, 0, 0, 0,
    0, 8, 0, 0,
    0, 0, 0, 0,
    0, 0, 8, 0,
    8, 8, 0, 0,
    0, 0, 0, 0,
])

ack_state = False

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

main()
