# Opal Nugget Ice BLE Integration
Home Assistant BLE Integration for FirstBuild Opal Nugget Ice Maker.

I am still working on adding switches to turn on/off light and icemaker. If you want switch capability, use the ESPHome code posted below.

This might work for the GE Branded model, not sure. Mine is the OG FirstBuild version

References:

@shmuelzon https://github.com/shmuelzon/esp32-ble2mqtt/wiki/Opal-(GE)-Ice-Maker

@SirSmith ESPHome version: https://community.home-assistant.io/t/json-to-yaml-conversion-for-ge-opal

### Installation Instructions
- Add this repo into HACS
- Install integration
- Restart Homeassistant
- Wait a few minutes and HA should find it automatically
- If not found automatically, Go to Settings->Device and Services->Add Integration (blue button at bottom right) -> search for Opal BLE
- It should find it and set it up

Another option is to use ESPHome (but less effecient). However, this supports switches
```
esphome:
  name: esphome-web-XXXXX
  friendly_name: ESP32Proxy

esp32:
  board: esp32dev
  framework:
    type: esp-idf

logger:
  level: DEBUG

# Enable Home Assistant API
api:
  encryption:
    key: XXXXXXXX
    
ota:

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

esp32_ble_tracker:
  scan_parameters:
    active: True

bluetooth_proxy:
  active: True

ble_client:
  - mac_address: 'XX:XX:XX:XX:XX:XX'
    id: ice_maker
    on_passkey_request:
      then:
        - ble_client.passkey_reply:
            id: ice_maker
            passkey: 000000
    on_connect:
      then:
        - lambda: |-
            ESP_LOGD("ble_client_lambda", "Connected to Opal Ice Maker");
            id(ice_maker)->pair();
    on_disconnect:
      then:
        - lambda: |-
            ESP_LOGD("ble_client_lambda", "Disconnected from Opal Ice Maker");

sensor:
  - platform: ble_client
    ble_client_id: ice_maker
    name: "Make State"
    id: make_state
    service_uuid: '3e6763c5-9429-40cc-909e-bebf8c7487be'
    characteristic_uuid: '097a2751-ca0d-432f-87b5-7d2f31e45551'
    type: characteristic
  - platform: ble_client
    ble_client_id: ice_maker
    name: "Ice Bin State"
    service_uuid: '3e6763c5-9429-40cc-909e-bebf8c7487be'
    characteristic_uuid: '5bcbf6b1-de80-94b6-0f4b-99fb984707b6'
    type: characteristic
  - platform: ble_client
    ble_client_id: ice_maker
    name: "Night Mode"
    id: night_mode
    service_uuid: '3e6763c5-9429-40cc-909e-bebf8c7487be'
    characteristic_uuid: '37988f00-ea39-4a2d-9983-afad6535c02e'
    type: characteristic

switch:
  - platform: template
    name: "Night Mode Switch"
    lambda: |-
      if (id(night_mode).state) {
        return true;
      } else {
        return false;
      }
    turn_on_action:
      - ble_client.ble_write:
          id: ice_maker
          service_uuid: '3e6763c5-9429-40cc-909e-bebf8c7487be'
          characteristic_uuid: '37988f00-ea39-4a2d-9983-afad6535c02e'
          # List of bytes to write.
          value: [0x01]
    turn_off_action:
      - ble_client.ble_write:
          id: ice_maker
          service_uuid: '3e6763c5-9429-40cc-909e-bebf8c7487be'
          characteristic_uuid: '37988f00-ea39-4a2d-9983-afad6535c02e'
          # List of bytes to write.
          value: [0x00]
  - platform: template
    name: "Make Ice Switch"
    lambda: |-
      if (id(make_state).state == 1 ) {
        return true;
      } else {
        return false;
      }
    turn_on_action:
      - ble_client.ble_write:
          id: ice_maker
          service_uuid: '3e6763c5-9429-40cc-909e-bebf8c7487be'
          characteristic_uuid: '79994230-4b04-40cd-85c9-02dd1a8d4dd0'
          # List of bytes to write.
          value: [0x01]
    turn_off_action:
      - ble_client.ble_write:
          id: ice_maker
          service_uuid: '3e6763c5-9429-40cc-909e-bebf8c7487be'
          characteristic_uuid: '79994230-4b04-40cd-85c9-02dd1a8d4dd0'
          # List of bytes to write.
          value: [0x00]
```

 
