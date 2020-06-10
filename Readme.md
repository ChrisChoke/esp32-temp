# ESP32-Temp

## Instructions

A few simple lines to read the temperature from multiple ds18x20 sensors on a ESP32 board with micropython and publish it via mqtt to your mqtt-broker.

### boot.py:

Perpare all variables getting from config.json and connect to your WiFi.

### main.py:

Includes the Main code.

### config.json:

The `config.json` includes your configuration in json-format. The config in the `config.json` of the repo includes all important config keywords.

possible configs:

```
{
    "ssid" : "YOUR_SSID",
    "password" : "YOUR_PASSWORD",
    "machinePin" : 32,
    "mqttServer" : "IP_ADDRESS",
    "mqttPort" : 1111,              // default 1883
    "mqttUser" : "USERNAME",        // default None
    "mqttPasswd" : "PASSWORD",      // default None
    "ntp": "IP_ADDRESS or DNS",     // default None
    "topicPub" : "esp32/"           // default "esp32/"
}
```
### devices.json

The devices.json includes all connected ds18x20 sensors. The sensors will automaticliy append to this file on startup and you get information with mqtt message at esp32/system if new sensors are found.
You can download devices.json from the board and put a friendlyName in the value section and put it back to the board, or creating a readable json file with the bytearray and a friendlyName and put it to the board. The bytearray you can copy from the mqtt message how explained above.
Its recommend to do that, because the sensors will provide as bytearray. It looks a bit ugly for the mqtt topic and can generated another subtopic if there is a "/" in the bytearray.

### MQTT

you will get following mqtt topics:

#### esp32/timestamp
get a timestamp from last transmission to mqtt-broker formattet in:

dd.mm.yyyy hh:mm:ss

#### esp32/system/state
get the connection state to mqtt-broker:</br>

'Online' or </br>
'Offline'

#### esp32/system/linkquality
get the wifi quality as rssi.

#### esp32/friendlyName/temperature
get the temperature of the ds18x20 sensors in °C