import utime
import ntptime
import ujson
from umqtt.simple import MQTTClient
import uasyncio
from microdot_asyncio import Microdot, Response
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

configRead = open('config.json').read()
config = ujson.loads(configRead)

ssid = config["ssid"]
password = config["password"]
machinePin = config["machinePin"]
mqttServer = config["mqttServer"]
mqttPort = config["mqttPort"] if "mqttPort" in config else 1883
mqttUser = config["mqttUser"] if "mqttUser" in config else None
mqttPasswd = config["mqttPasswd"] if "mqttPasswd" in config else None
clientId = ubinascii.hexlify(machine.unique_id())
#topicSub = 'esp32/Temperature/data/'
topicPub = config["topicPub"] if "topicPub" in config else 'esp32/'
ntp = config["ntp"] if "ntp" in config else None

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

ntptime.host = ntp