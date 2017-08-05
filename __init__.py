import ugfx, gc, wifi, badge, deepsleep, urandom
from time import *

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
    sleep(0.1)
    pass

ugfx.clear(ugfx.WHITE);
ugfx.string(10,10,"Connecting to MQTT...","Roboto_Regular12", 0)
ugfx.flush()

from umqtt.simple import MQTTClient

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print((topic, msg))

    topic_txt = topic.decode('utf-8')
    text = msg.decode('utf-8')

    if text.lower() == "on":
        badge.leds_send_data(bytes([
            64, 0, 0, 0,
            0, 64, 0, 0,
            0, 0, 64, 0,
            0, 64, 64, 0,
            64, 64, 0, 0,
            64, 0, 64, 0,
        ]), 24)
    elif text.lower() == "off":
        badge.leds_send_data(bytes([
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
        ]), 24)

    ugfx.clear(ugfx.WHITE)
    ugfx.flush()
    ugfx.string(50,10,"badgepager","Roboto_BlackItalic24",ugfx.BLACK)
    ugfx.string(50,25,text,"Roboto_BlackItalic24",ugfx.BLACK)
    ugfx.string(50,40,topic_txt,"Roboto_BlackItalic24",ugfx.BLACK)
    ugfx.flush()

def main(server="test.mosquitto.org"):
    clientname = 'SHA2017SWE ' + str(urandom.getrandbits(30))
    c = MQTTClient(clientname, server)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(b"sha2017pager/swe/MA:CK:AD:DR:SS")

    c.check_msg()
    while True:
        c.check_msg()
        sleep(1)
    c.disconnect()

def go_home(pushed):
    if(pushed):
        import machine
        machine.deepsleep(1)

ugfx.input_attach(ugfx.BTN_B, go_home)
main()