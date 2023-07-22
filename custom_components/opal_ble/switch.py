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
    async_add_entities([OpalNightModeSwitch(coordinator,coordinator.data)])

class OpalNightModeSwitch(CoordinatorEntity[DataUpdateCoordinator[OpalDevice]], SwitchEntity):
    
    _attr_device_class = SwitchDeviceClass.SWITCH
    
    def __init__(self, coordinator: DataUpdateCoordinator,opal_device: OpalDevice) -> None:
        """Initialize the Switchbot."""
        
        super().__init__(coordinator)
        self._attr_is_on = False
    
    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
    @property
    def is_on(self) -> bool | None:
        """Return true if device is on."""
        #return self._device._nightMode
        return True

    async def async_turn_on(self, **kwargs):
        self._device.night_mode_on()

    async def async_turn_off(self, **kwargs):
        self._device.night_mode_off()