def connect_and_subscribe():
  global clientId, mqttServer, topicSub
  client = MQTTClient(clientId, mqttServer, port=mqttPort, user=mqttUser, password=mqttPasswd)
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

try:
  client = connect_and_subscribe()
except OSError as e:
  print('An exception has occured: '+ str(e))
  restart_and_reconnect()

if ntp != None:
  ntptime.settime()
dsPin = machine.Pin(machinePin)
dsSensor = ds18x20.DS18X20(onewire.OneWire(dsPin))

roms = dsSensor.scan()
romsConvDict = { str(i) : str(i) for i in roms}
print('Found DS devices: ', roms)

try:
    devicesRead = open('devices.json').read()
except OSError:
    createDevicesFile = open('devices.json', 'w')
    createDevicesFile.write(ujson.dumps({}))
    createDevicesFile.close()
    devicesRead = open('devices.json').read()

devicesJson = ujson.loads(devicesRead)
print(devicesJson)
for x in romsConvDict:
  newDevicesPub = []
  if x in devicesJson:
    print(x + 'bereits in devices.json')
  else:
    devicesJson[x] = x
    devicesAppend = open('devices.json', 'w')
    devicesAppend.write(ujson.dumps(devicesJson))
    devicesAppend.close()
    newDevicesPub.append(x)
    client.publish(topicPub+'system', 'New Sensors found and added to devices.json: '+ str(newDevicesPub))

while True:
  try:
    dsSensor.convert_temp()
    utime.sleep_ms(750)
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
    utime.sleep(5)
  except OSError as e:
    print('An exception has occured: '+ str(e))
    restart_and_reconnect()
  except onewire.OneWireError as e:
    print('An exception has occured: '+ repr(e))
    restart_and_reconnect()
