import json
import gc


def create_playload(name, base_topic: str, ow_address: str, friendly_name: str) -> dict:
   return {
      "name": f"{friendly_name}",
      "device_class": "temperature",
      "state_class": "measurement",
      "state_topic": f"{base_topic}{friendly_name}/temperature",
      "unit_of_measurement": "\u00b0C",
      "value_template": "{{ value }}",
      "unique_id": f"{ow_address}_temp",
      "device": {
         "identifiers": [
            f"esp32_{name}"
         ],
         "name": f"{name}",
      }
   }
async def home_assistant(client, name: str, base_topic: str, devices: dict):
   capital_name = f'{name[0].upper()}{name[1:]}'
   
   for index, (ow_address, friendly_name) in enumerate(devices.items()):
      
      sensor_payload = (create_playload(capital_name, base_topic, ow_address, friendly_name))
      
      haTopicm3= f'homeassistant/sensor/esp32{capital_name}/temperature_{index}/config'
      
      json_payload_m3 = json.dumps(sensor_payload).encode('utf8') # need encoding for degree sign
      await client.publish(f'{haTopicm3}', json_payload_m3, retain=True)
      gc.collect()