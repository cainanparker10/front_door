from network import WLAN      # For operation of WiFi network
import time                   # Allows use of time.sleep() for delays
import pycom                  # Base library for Pycom devices
from umqtt import MQTTClient  # For use of MQTT protocol to talk to Adafruit IO
import ubinascii              # Needed to run any MicroPython code
import machine                # Interfaces with hardware components
from machine import Pin
import micropython            # Needed to run any MicroPython code

# Wireless network
WIFI_SSID = "FTPSolutions_Operational"
WIFI_PASS = "_ftP0p3r@t10n@l" 

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "CainanParker10"
AIO_KEY = "43ec3e3dd6ec40a1a09d726663db0cee"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_CONTROL_FEED = "CainanParker10/feeds/front-door"

# RGBLED
# Disable the on-board heartbeat (blue flash every 4 seconds)
# We'll use the LED to respond to messages from Adafruit IO
pycom.heartbeat(False)
time.sleep(1) # Workaround for a bug.
                # Above line is not actioned if another
                # process occurs immediately afterwards
pycom.rgbled(0xff0000)  # Status red = not working

# WIFI

wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_SSID, auth=(WLAN.WPA2, WIFI_PASS), timeout=5000)
while not wlan.isconnected():    # Code waits here until WiFi connects
    machine.idle()
print("Connected to Wifi")

# FUNCTIONS
def relay_on():
    p_out = Pin('P23', mode=Pin.OUT)
    p_out.value(1)
    pycom.rgbled(0xFF0000) # Red
    time.sleep(10)
    p_out.value(0)
    pycom.rgbled(0x00FF00) # Green

# Function to respond to messages from Adafruit IO
def sub_cb(topic, msg):          # sub_cb means "callback subroutine"
    print((topic, msg))          # Outputs the message that was received. Debugging use.
    if msg == b"1":             # If message says "ON" ...
        relay_on()
    else:                        # If any other message is received ...
        print("Unknown message") # ... do nothing but output that it happened.

client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)

client.set_callback(sub_cb)
client.connect()
client.subscribe(AIO_CONTROL_FEED)

print("Connected to %s, subscribed to %s topic" % (AIO_SERVER, AIO_CONTROL_FEED))

pycom.rgbled(0x00ff00) # Status green: online to Adafruit IO

try:                      # Code between try: and finally: may cause an error
                          # so ensure the client disconnects the server if
                          # that happens.
    while 1:              # Repeat this loop forever
        client.check_msg()# Action a message if one is received. Non-blocking.
finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    wlan.disconnect()
    wlan = None
    pycom.rgbled(0x000022) # Status blue: stopped
    print("Disconnected from Adafruit IO.")
