# import microdot early to alloc needed memory
from microdot import Microdot, Response
from microdot.utemplate import Template
from mqtt_as import MQTTClient, config
from homeassistant import home_assistant

import gc
gc.collect()

import time
import ntptime
import json
from sys import platform
import asyncio
import micropython
import machine
import onewire
import ds18x20
import esp
esp.osdebug(None)
gc.collect()

def dumpJson(jsonData: dict, fileName: str):
  """
  simply dump dictionary to json file
  """
  wDevices = open(fileName, 'w')
  wDevices.write(json.dumps(jsonData))
  wDevices.close()

def checkDeviceAlive(owDevices: list, jsonData: dict) -> list:
  """
  check if devices.json contains oneWire devices are in scanned list to check if 
  devices.json is up to date

  return list of missing devices
  """
  missingDevices = []
  for key in jsonData:
    if key in owDevices:
      continue
    else:
      missingDevices.append(key)
  return missingDevices

def rom2str(rom: bytearray) -> str:
        return ''.join('%02X' % i for i in iter(rom))

def str2rom(rom: str) -> bytearray:
    a = bytearray(8)
    for i in range(8):
        a[i] = int(rom[i * 2:i * 2 + 2], 16)
    return a

async def continousTempPublish(client):
  while True:
    try:
      dsSensor.convert_temp()
      await asyncio.sleep_ms(750)
      for rom in romsId:
        friendlyName = devicesJson[rom] if rom in devicesJson else rom
        readTemp = dsSensor.read_temp(str2rom(rom))
        tempRounded = '{0:.2f}'.format(readTemp)
        print(friendlyName)
        print(tempRounded)
        if ntp != None:
          timestamp = time.localtime()
          await client.publish(topicPub+'timestamp', str('{:02}'.format(timestamp[2]))+'.'+str('{:02}'.format(timestamp[1]))+'.'+str(timestamp[0])+' '+str('{:02}'.format(timestamp[3]+2))+':'+str('{:02}'.format(timestamp[4]))+':'+str('{:02}'.format(timestamp[5])))
        else:
          await client.publish(topicPub+'timestamp', 'ntp not defined')
        await client.publish(topicPub+friendlyName+'/temperature', tempRounded)
        #await client.publish(topicPub+'system/linkquailty', str(station.status('rssi')))
      asyncio.create_task(pulse())
      gc.collect()
      await asyncio.sleep_ms(5000)
    except OSError as e:
      print('An exception has occured: '+ str(e))
      machine.reset()
    except onewire.OneWireError as e:
      print('An exception has occured: '+ repr(e))
      machine.reset()
    except Exception as e:
      # catching crc exception to keep script running
      print('An exception has occured: '+ str(e))
      await client.publish(topicPub+'system/errors', str(e))

async def pulse():
  """
  let pulse the blue led
  """
  blue_led(False)
  await asyncio.sleep(1)
  blue_led(True)

async def down(client):
  """
  coroutine for connection down
  """
  while True:
      await client.down.wait()  # Pause until connectivity changes
      client.down.clear()
      wifi_led(False)
      print('WiFi or broker is down.')

async def up(client):
  """
  coroutine for connection up
  """
  while True:
      await client.up.wait()
      client.up.clear()
      wifi_led(True)
      await client.publish(f'{topicPub}system/state', 'Online')
      asyncio.create_task(pulse())

async def main(client):

  await client.connect()
  if ntp != None:
    ntptime.settime()
  
  # publish to mqtt new and missing devices if list not empty
  if newDevicesPub:
    print('new devices: ', newDevicesPub)
    await client.publish(topicPub+'system', 'New Sensors found and added to devices.json: '+ str(newDevicesPub))
  
  if missingDev:
    print('missing devices: ', missingDev)
    await client.publish(topicPub+'system', 'Some Sensors from devices.json are missing: '+ str(missingDev))

  if homeAssistant and name:
    allived_devs = {k:devicesJson[k] for k in devicesJson if not k in missingDev}  # announce only living sensors to ha
    await home_assistant(client, name, topicPub, allived_devs)
  asyncio.create_task(continousTempPublish(client))
  
def start_async_app():
  gc.collect()
  loop= asyncio.get_event_loop()
  for task in (up, down, main):
        loop.create_task(task(client))
  loop.create_task(app.start_server(port=80))
  loop.run_forever()

########## entry point ##########

gc.collect()

# merge mqtt_as config with our config.json for defaulting some settings
configRead = open('config.json').read()
configJson = json.loads(configRead)
config.update(configJson)

topicPub = config["topicPub"] if "topicPub" in config else 'esp32Temp/'
homeAssistant = config["homeassistant"] if "homeassistant" in config else False
name = config["name"] if "name" in config else None
ntp = config["ntp"] if "ntp" in config else None

ntptime.host = ntp

config["queue_len"] = 1
config['will'] = ( f'{topicPub}system/state', 'Offline', False, 0 )
MQTTClient.DEBUG = True
client = MQTTClient(config)

# set up webrepl if password in config.json
if config["webreplpw"]:
    try:
        import webrepl_cfg
    except ImportError:
        try:
            with open("webrepl_cfg.py", "w") as f:
                f.write("PASS = %r\n" % config["webreplpw"])
        except Exception as e:
            print("Can't start webrepl: {!s}".format(e))
    try:
        import webrepl

        webrepl.start()
    except Exception as e:
        print("Can't start webrepl: {!s}".format(e))

# setup red and blue led which can connected to the board
if platform == 'esp8266' or platform == 'esp32':
    from machine import Pin
    def ledfunc(pin, active=0):
        pin = pin
        def func(v):
            pin(not v)  # Active low on ESP8266
        return pin if active else func
    wifi_led = ledfunc(Pin(0, Pin.OUT, value = 1))  # Red LED for WiFi fail/not ready yet
    blue_led = ledfunc(Pin(2, Pin.OUT, value = 0))  # Message send


dsPin = machine.Pin(config['machinePin'])
dsSensor = ds18x20.DS18X20(onewire.OneWire(dsPin))

# scan dsSensors on board
roms = dsSensor.scan()
romsId = [rom2str(i) for i in roms] # create Id list with strings
romsIdDict = { i : i for i in romsId}
print('Found DS devices: ', romsId)

try:
    devicesRead = open('devices.json').read()
except OSError:
    dumpJson({}, 'devices.json')
    devicesRead = open('devices.json').read()

# load devices.json and check if new device is found and add to devices.json
devicesJson = json.loads(devicesRead)
newDevicesPub = []
for x in romsIdDict:
  if x in devicesJson:
    print(x + ' already exist in devices.json')
  else:
    devicesJson[x] = x
    newDevicesPub.append(x)

# sort dict by keys. On every boot the order was different
sort_devices = sorted(devicesJson.items())
sorted_devices = {k: v for k, v in sort_devices}
devicesJson = sorted_devices
dumpJson(devicesJson, 'devices.json')

missingDev = checkDeviceAlive(romsId, devicesJson)

# create webserver
app = Microdot()
Response.default_content_type = 'text/html'

@app.route('/', methods=['GET', 'POST'])
async def mainSite(request):
  if request.method == "POST":
    if "change" in request.form:
      for key in request.form:
        if key == 'change':
          continue
        else:
          devicesJson[key] = request.form[key]
      dumpJson(devicesJson, 'devices.json')
    elif "reboot" in request.form:
      machine.reset()
    elif "rm" in request.form:
      rmKey = request.form['rm']
      devicesJson.pop(rmKey)
      missingDev.remove(rmKey)
      dumpJson(devicesJson, 'devices.json')
  return await Template('index.tpl').render_async(devices=devicesJson, missingDevlist=missingDev)

try:
  start_async_app()
except:
  app.shutdown()
  client.close()
  blue_led(True)