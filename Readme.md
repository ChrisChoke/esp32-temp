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

```json
{
"ssid" : "YOUR_SSID",
"password" : "YOUR_PASSWORD",
"machinePin" : 32,
"mqttServer" : "IP_ADDRESS",
"mqttPort" : 1111,              // default 1883
"mqttUser" : "USERNAME",        // default None
"mqttPasswd" : "PASSWORD",      // default None
"ntp": "IP_ADDRESS or DNS",     // default None
"topicPub" : "esp32/"           // default "esp32"
}
```