"""Support for opal ble sensors."""
from __future__ import annotations

import logging

from .opal_ble import OpalDevice

from homeassistant import config_entries
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import DOMAIN, VOLUME_BECQUEREL, VOLUME_PICOCURIE

_LOGGER = logging.getLogger(__name__)

SENSORS_MAPPING_TEMPLATE: dict[str, SensorEntityDescription] = {
    "make_state": SensorEntityDescription(
        key="make_state",
        name="Ice Maker State",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:radioactive",
    ),
    "make_state_string": SensorEntityDescription(
        key="make_state_string",
        name="Ice Maker State Names",
        state_class=None,
        icon="mdi:radioactive",
    ),
    "ice_bin_state": SensorEntityDescription(
        key="ice_bin_state",
        name="Ice Bin State",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:radioactive",
    ),
    "cleaning_phase": SensorEntityDescription(
        key="cleaning_phase",
        name="Cleaning Phase",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:radioactive",
    ),
    "night_mode": SensorEntityDescription(
        key="night_mode",
        name="Night Mode",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:radioactive",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Opal BLE sensors."""
    is_metric = hass.config.units is METRIC_SYSTEM

    coordinator: DataUpdateCoordinator[OpalDevice] = hass.data[DOMAIN][entry.entry_id]
    sensors_mapping = SENSORS_MAPPING_TEMPLATE.copy()
    entities = []
    _LOGGER.debug("got sensors: %s", coordinator.data.sensors)
    for sensor_type, sensor_value in coordinator.data.sensors.items():
        if sensor_type not in sensors_mapping:
            _LOGGER.debug(
                "Unknown sensor type detected: %s, %s",
                sensor_type,
                sensor_value,
            )
            continue
        entities.append(
            OpalSensor(coordinator, coordinator.data, sensors_mapping[sensor_type])
        )

    async_add_entities(entities)


class OpalSensor(CoordinatorEntity[DataUpdateCoordinator[OpalDevice]], SensorEntity):
    """Opal BLE sensors for the device."""

    #_attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        opal_device: OpalDevice,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Populate the opal entity with relevant data."""
        super().__init__(coordinator)
        self.entity_description = entity_description

        name = f"{opal_device.name} {opal_device.identifier}"

        self._attr_unique_id = f"{name}_{entity_description.key}"

        self._id = opal_device.address
        self._attr_device_info = DeviceInfo(
            connections={
                (
                    CONNECTION_BLUETOOTH,
                    opal_device.address,
                )
            },
            name=name,
            manufacturer="Opal",
            model="Opal",
            hw_version=opal_device.hw_version,
            sw_version=opal_device.sw_version,
        )

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        try:
            return self.coordinator.data.sensors[self.entity_description.key]
        except KeyError:
            return None
