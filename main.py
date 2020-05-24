if ntp != None:
  ntptime.settime()
dsPin = machine.Pin(machinePin)
dsSensor = ds18x20.DS18X20(onewire.OneWire(dsPin))

roms = dsSensor.scan()
print('Found DS devices: ', roms)

def connect_and_subscribe():
  global clientId, mqttServer, topicSub
  client = MQTTClient(clientId, mqttServer, port=mqttPort, user=mqttUser, password=mqttPasswd)
  client.connect()
  print('Connected to %s MQTT broker' % (mqttServer))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  utime.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    dsSensor.convert_temp()
    utime.sleep_ms(750)
    for rom in roms:
      serialnum = hex(int.from_bytes(rom, 'little'))
      print(serialnum)
      print(dsSensor.read_temp(rom))
      if ntp != None:
        timestamp = utime.localtime()
        client.publish(topicPub+'timestamp', str('{:02}'.format(timestamp[2]))+'.'+str('{:02}'.format(timestamp[1]))+'.'+str(timestamp[0])+' '+str('{:02}'.format(timestamp[3]+2))+':'+str('{:02}'.format(timestamp[4]))+':'+str('{:02}'.format(timestamp[5])))
      else:
        client.publish(topicPub+'timestamp', 'ntp not defined')
      client.publish(topicPub+serialnum+'/temperature', str(dsSensor.read_temp(rom)))
    utime.sleep(5)
  except OSError as e:
    restart_and_reconnect()
