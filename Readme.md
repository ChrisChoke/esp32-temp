# ESP32-Temp

## Instructions

**Micropython >= 1.21**

A few simple lines to read the temperature from multiple ds18x20 sensors on a ESP32 board with micropython and publish it via mqtt to your mqtt-broker.
This little software contains a Website to configure friendly-names for the sensors, reboot the esp or delete missing devices from devices.json.

### boot.py:

Empty

### main.py:

Includes the Main code.

You can connect on Pin 0 a red LED and on Pin 2 a blue LED to check if wifi is down (red led turn on) and if a
mqtt message is sent (blue led pulse for 1 sec)

wifi_led = ledfunc(Pin(0, Pin.OUT, value = 1))  # Red LED for WiFi fail/not ready yet
blue_led = ledfunc(Pin(2, Pin.OUT, value = 0))  # Message send

### config.json:

The `config.json` includes your configuration in json-format. The config in the `config.json` of the repo includes all important config keywords.

possible configs:

```
{
    "ssid" : "YOUR_SSID",
    "wifi_pw" : "YOUR_PASSWORD",
    "machinePin" : 32,
    "server" : "IP_ADDRESS",
    "port" : 1111,              // default 1883
    "user" : "USERNAME",        // default None
    "password" : "PASSWORD",      // default None
    "ntp": "IP_ADDRESS or DNS",     // default None
    "topicPub" : "esp32/",           // default "esp32/"
    "webreplpw": "MYPASSWORD", // webreplpassword need to configure webrepl
    "homeassistant": true,  // default false
    "name": "heater"    // default None, needs in combination with homeassistant for device name
}
```
### devices.json

The devices.json includes all connected ds18x20 sensors. The sensors will automaticliy append to this file on startup and you get information with mqtt message at esp32/system if new sensors are found.

You can set a friendly name for each temperature sensor via website.
On this website you can remove old sensors which aren't on the onewire-bus anymore.

**hint:** For the ds18x20 you need a pull-up resistor to read values from it. Most tutorials recommended a 4k7 resistor. In my build, i have 8 sensor running and i needed approximately 1k5 ohm. With bigger resistant not all sensors were identified on the bus.

### MQTT

you will get following mqtt topics:

#### esp32/timestamp
get a timestamp from last transmission to mqtt-broker formattet in:

dd.mm.yyyy hh:mm:ss

#### esp32/system/state
get the connection state to mqtt-broker:</br>

'Online' or </br>
'Offline'

#### esp32/friendlyName/temperature
get the temperature of the ds18x20 sensors in °C