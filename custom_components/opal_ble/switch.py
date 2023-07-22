"""Support for Switchbot bot."""
from __future__ import annotations

import logging
from typing import Any

from .opal_ble import OpalDevice, OpalBluetoothDeviceData

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

# Initialize the logger
_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Switchbot based on a config entry."""
    coordinator: DataUpdateCoordinator[OpalDevice] = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OpalNightModeSwitch(coordinator)])
    _LOGGER.debug(coordinator.data)
    _LOGGER.debug("Making Switch: async_setup_entry ")

class OpalNightModeSwitch(CoordinatorEntity[DataUpdateCoordinator[OpalDevice]], SwitchEntity):
    
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_has_entity_name = True
    
    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize the Switchbot."""
        super().__init__(coordinator)
        self._attr_is_on = False
        _LOGGER.debug("Init Switch")
         
    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
    @property
    def is_on(self) -> bool | None:
        """Return true if device is on."""
        #return self._device._nightMode
        _LOGGER.debug("is_on")
        return True

    async def async_turn_on(self, **kwargs):
        return
        #await self._device.night_mode_on()

    async def async_turn_off(self, **kwargs):
        return
        #await self._device.night_mode_off()