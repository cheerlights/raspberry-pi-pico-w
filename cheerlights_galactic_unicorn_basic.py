import WIFI_CONFIG
from network_manager import NetworkManager

import uasyncio
import urequests
import time
from machine import Timer, Pin
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

# Galactic Unicorn settings
gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

# Raspberry Pi Pico W settings
status_led = Pin('LED', Pin.OUT)

# CheerLights settings for ThingSpeak
URL = 'http://api.thingspeak.com/channels/1417/field/2/last.json'
UPDATE_INTERVAL = 5

# CheerLights defaults
cheerlights_hex = '#000000'
cheerlights_r = 0
cheerlights_g = 0
cheerlights_b = 0

# define helper functions
def status_handler(mode, status, ip):
    print(mode, status, ip)
    print('Connecting to Wi-Fi...')
    if status is not None:
        if status:
            print('Wi-Fi connection successful!')
        else:
            print('Wi-Fi connection failed!')
            
def gradient(r, g, b):
    for y in range(0, height):
        for x in range(0, width):
            graphics.set_pen(graphics.create_pen(int((r * x) / 52), int((g * x) / 52), int((b * x) / 52)))
            graphics.pixel(x, y)

def hex_to_rgb(hex):
    # converts a hex code into RGB
    h = hex.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return r, g, b

def get_cheerlights_color():
    # open a request to thingspeak for the json feed
    cheerlights_request = urequests.get(URL)
    cheerlights_json = cheerlights_request.json()
    cheerlights_request.close()

    # flash the onboard LED after getting data
    status_led.value(True)
    time.sleep(0.2)
    status_led.value(False)

    # extract hex value from the json data
    cheerlights_hex = cheerlights_json['field2']
    print(f'CheerLights HEX: {cheerlights_hex}')

    # calculate the red, green, and blue color values
    cheerlights_r, cheerlights_g, cheerlights_b = hex_to_rgb(cheerlights_hex)

    # update the LED panel
    update_graphics(cheerlights_r, cheerlights_g, cheerlights_b)
    
def update_graphics(r, g, b):
    gradient(r, g, b)
    gu.update(graphics)

# connect to Wi-Fi
try:
    network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)
    uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))
except Exception as e:
    print(f'Wi-Fi connection failed! {e}')

# get the latest cheerlights color
get_cheerlights_color()

# start timer and call get_cheerlights_color based on the UPDATE_INTERVAL setting
timer = Timer(-1)
timer.init(period=UPDATE_INTERVAL * 1000, mode=Timer.PERIODIC, callback=lambda t: get_cheerlights_color())

while True:

    # pause for a moment (important or the USB serial device will fail)
    time.sleep(0.001)