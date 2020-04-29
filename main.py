

ds_pin = machine.Pin(32)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

roms = ds_sensor.scan()
print('Found DS devices: ', roms)

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, port=mqtt_port, user=mqtt_user, password=mqtt_passwd)
  client.connect()
  print('Connected to %s MQTT broker' % (mqtt_server))
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
    ds_sensor.convert_temp()
    utime.sleep_ms(750)
    for rom in roms:
      serialnum = hex(int.from_bytes(rom, 'little'))
      print(serialnum)
      print(ds_sensor.read_temp(rom))
      client.publish(topic_pub+serialnum+'/temperature', str(ds_sensor.read_temp(rom)))
    utime.sleep(5)
  except OSError as e:
    restart_and_reconnect()