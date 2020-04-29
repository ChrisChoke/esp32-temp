# ESP32-Temp

## Instructions

A few simple lines to read the temperature from multiple ds18x20 sensors on a ESP32 board with micropython and publish it via mqtt to your mqtt-broker.

### boot.py:

Just change with your own proberties in the variables of: ```ssid```, ```password```, ```mqtt_server```, ```mqtt_user```, ```mqtt_passwd```

### main.py:

Change the pin number at ```ds_pin = machine.Pin(32)``` what you use.
