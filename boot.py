import utime
from umqtt.simple import MQTTClient
import ubinascii
import machine
import onewire
import ds18x20
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = 'YOUR_SSID'
password = 'YOUR_PASSWORD'
mqtt_server = 'IP_ADDRESS_BROKER'
mqtt_port = 1883
mqtt_user = 'USERNAME'
mqtt_passwd = 'PASSWORD'
client_id = ubinascii.hexlify(machine.unique_id())
# topic_sub = 'esp32/Temperature/data/'
topic_pub = 'esp32/'


station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
