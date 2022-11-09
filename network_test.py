import WIFI_CONFIG
from network_manager import NetworkManager

import uasyncio
import urequests
import time

URL = 'http://api.thingspeak.com/channels/1417/field/2/last.json'
UPDATE_INTERVAL = 5

def status_handler(mode, status, ip):
    print(mode, status, ip)
    print('Connecting to Wi-Fi...')
    if status is not None:
        if status:
            print('Wi-Fi connection successful!')
        else:
            print('Wi-Fi connection failed!')

try:
    network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)
    uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))
except Exception as e:
    print(f'Wi-Fi connection failed! {e}')

while True:
    print(f'Requesting URL: {URL}')
    cheerlights_request = urequests.get(URL)
    cheerlights_json = cheerlights_request.json()
    cheerlights_request.close()

    hex = cheerlights_json['field2']

    print(f'CheerLights HEX: {hex}')

    time.sleep(UPDATE_INTERVAL)
