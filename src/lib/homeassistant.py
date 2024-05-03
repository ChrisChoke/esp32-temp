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
   
   for ow_address, friendly_name in devices.items():
      
      ident = ow_address[-4:]
      sensor_payload = (create_playload(capital_name, base_topic, ow_address, friendly_name))
      
      haTopic= f'homeassistant/sensor/esp32{capital_name}/temperature_{ident}/config'
      
      json_payload = json.dumps(sensor_payload).encode('utf8') # need encoding for degree sign
      await client.publish(f'{haTopic}', json_payload, retain=True)
      gc.collect()

async def delete_from_ha(client, name: str, ow_address: str):
   capital_name = f'{name[0].upper()}{name[1:]}'
   ident = ow_address[-4:]

   haTopic= f'homeassistant/sensor/esp32{capital_name}/temperature_{ident}/config'
   json_payload = json.dumps({}).encode('utf8')  # send empty payload to delete from ha
   await client.publish(f'{haTopic}', json_payload, retain=True)