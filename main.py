import html

# some str() convertings are a bit weird in case there is some trouble with comparing bytearrays as string type with
# bytearray as string type which loaded from devices.json. ujson.dump() escapes "\" backslashes and if ujson.load()
# will put the escaped string in dictionary. so some comparings are "bytearray(b'(\xeeWV\xb5\x01<a')" vs "bytearray(b'(\\xeeWV\\xb5\\x01<a')"

def connect_and_subscribe():
  global clientId, mqttServer, topicSub
  client = MQTTClient(clientId, mqttServer, port=mqttPort, user=mqttUser, password=mqttPasswd, keepalive=30)
  client.set_last_will(topicPub+'system/state', 'Offline')
  client.connect()
  print('Connected to %s MQTT broker' % (mqttServer))
  client.publish(topicPub+'system/state', 'Online')
  return client

def restart_and_reconnect():
  try:
    client.publish(topicPub+'system/state', 'Offline')
  finally:
    print('Rebooting. . .')
    utime.sleep(10)
    machine.reset()

def dumpJson(jsonData: dict, fileName: str):
  """
  simply dump dictionary to json file
  """
  wDevices = open(fileName, 'w')
  wDevices.write(ujson.dumps(jsonData))
  wDevices.close()

def checkDeviceAlive(owDevices: list, jsonData: dict):
  """
  check if devices.json contains oneWire devices are in scanned list to check if 
  devices.json is up to date

  return list of missing devices
  """
  missingDevices = []
  convOwDevices = [ str(i) for i in owDevices ]
  for key in jsonData:
    if key in convOwDevices:
      continue
    else:
      missingDevices.append(key)
  return missingDevices

def buildWebsite(devices: dict, missingDevlist: list):
  webHtml = html.html
  for key, value in devices.items():
    webHtml = webHtml + "<tr>"
    webHtml = webHtml + '<td><input type="text" disabled value="' + key + '" class=""></td>'
    if key in missingDevlist:
      aliveDev= "missing"
      webHtml = webHtml + '<td><input type="text" disabled value="' + value + '" name="' + key + '" class=""></td>'
      webHtml = webHtml + '<td><button name="rm_'+ key + '" class="button rm">&times;</button></td>'
    else:
      aliveDev = "alive"
      webHtml = webHtml + '<td><input type="text" value="' + value + '" name="' + key + '" class=""></td>'
      webHtml = webHtml + '<td><i style="color:green;">' + aliveDev + '</i></td>'
    webHtml = webHtml + "</tr>"
  webHtml = webHtml + "</table>"
  webHtml = webHtml + '<button name="change" class="button">Change</button><button name="reboot" class="button button2">Reboot</button></form>'
  return webHtml

async def continousTempPublish():
  while True:
    try:
      dsSensor.convert_temp()
      await uasyncio.sleep_ms(750)
      for rom in roms:
        friendlyName = devicesJson[str(rom)] if str(rom) in devicesJson else str(rom)
        print(friendlyName)
        print(dsSensor.read_temp(rom))
        if ntp != None:
          timestamp = utime.localtime()
          client.publish(topicPub+'timestamp', str('{:02}'.format(timestamp[2]))+'.'+str('{:02}'.format(timestamp[1]))+'.'+str(timestamp[0])+' '+str('{:02}'.format(timestamp[3]+2))+':'+str('{:02}'.format(timestamp[4]))+':'+str('{:02}'.format(timestamp[5])))
        else:
          client.publish(topicPub+'timestamp', 'ntp not defined')
        client.publish(topicPub+friendlyName+'/temperature', str(dsSensor.read_temp(rom)))
        client.publish(topicPub+'system/linkquailty', str(station.status('rssi')))
      await uasyncio.sleep_ms(5000)
    except OSError as e:
      print('An exception has occured: '+ str(e))
      restart_and_reconnect()
    except onewire.OneWireError as e:
      print('An exception has occured: '+ repr(e))
      restart_and_reconnect()
    except Exception as e:
      # catching crc exception to keep script running
      print('An exception has occured: '+ str(e))
      client.publish(topicPub+'system/errors', str(e))
      #restart_and_reconnect()

def start_server():
    print('Starting microdot app')
    try:
        app.run(port=80)
    except:
        app.shutdown()

########## entry point ##########

try:
  client = connect_and_subscribe()
except OSError as err:
  print('An exception has occured: '+ str(err))
  restart_and_reconnect()

if ntp != None:
  ntptime.settime()
dsPin = machine.Pin(machinePin)
dsSensor = ds18x20.DS18X20(onewire.OneWire(dsPin))

# scan dsSensors on board
roms = dsSensor.scan()
romsConvDict = { str(i) : str(i) for i in roms}
print('Found DS devices: ', roms)

try:
    devicesRead = open('devices.json').read()
except OSError:
    dumpJson({}, 'devices.json')
    devicesRead = open('devices.json').read()

# load devices.json and check if new device is found and add to devices.json
devicesJson = ujson.loads(devicesRead)
newDevicesPub = []
for x in romsConvDict:
  if x in devicesJson:
    print(x + 'already exist in devices.json')
  else:
    devicesJson[x] = x
    newDevicesPub.append(x)
dumpJson(devicesJson, 'devices.json')

# publish to mqtt new and missing devices if list not empty
if newDevicesPub:
  print('new devices: ', newDevicesPub)
  client.publish(topicPub+'system', 'New Sensors found and added to devices.json: '+ str(newDevicesPub))
missingDev = checkDeviceAlive(roms, devicesJson)
if missingDev:
  print('missing devices: ', missingDev)
  client.publish(topicPub+'system', 'Some Sensors from devices.json are missing: '+ str(missingDev))

# create webserver
app = Microdot()
current_task = None

@app.before_request
async def pre_request_handler(request):
  if current_task:
    current_task.cancel()

@app.route('/', methods=['GET', 'POST'])
async def mainSite(request):
  global current_task, buildHtml
  if request.method == "POST":
    if "change" in request.form:
      for key in request.form:
        if key.startswith('bytearray'):
          devicesJson[key] = request.form[key]
      dumpJson(devicesJson, 'devices.json')
    if "reboot" in request.form:
      restart_and_reconnect()
    # weird solution below to get removing keys. but no other idea for now
    # other solution with name="rm" value="bytearrayXXX" as string in html
    # did not work. KeyError will raised at devicesJson.pop()
    rmKey = list(request.form.keys())
    for key in rmKey:
      if key.startswith('rm_'):
        devicesJson.pop(key[3:])
        missingDev.remove(key[3:])
        dumpJson(devicesJson, 'devices.json')
        break
  buildHtml = buildWebsite(devicesJson, missingDev)
  current_task = uasyncio.create_task(continousTempPublish())
  return Response(body=buildHtml, headers={'Content-Type': 'text/html'})

current_task = uasyncio.create_task(continousTempPublish())
start_server()