"""Parser for Opal BLE devices"""

from __future__ import annotations

import asyncio
import dataclasses
import struct
from collections import namedtuple
from datetime import datetime
import logging

# from logging import Logger
from math import exp
from typing import Any, Callable, Tuple

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

from .const import (
    BQ_TO_PCI_MULTIPLIER,
)

NIGHT_MODE = "37988f00-ea39-4a2d-9983-afad6535c02e"
MAKE_ICE = "79994230-4b04-40cd-85c9-02dd1a8d4dd0"
MAKE_STATE = "097a2751-ca0d-432f-87b5-7d2f31e45551"
ICEBIN_STATE = "5bcbf6b1-de80-94b6-0f4b-99fb984707b6"
CLEANING_PHASE = "efe4bd77-0600-47d7-b3f6-dc81af0d9aaf"

OFF_VALUE = b"\x00"
ON_VALUE =  b"\x01"


_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class OpalDevice:
    """Response data with information about the Opal device"""

    hw_version: str = ""
    sw_version: str = ""
    name: str = ""
    identifier: str = ""
    address: str = ""
    sensors: dict[str, str | float | None] = dataclasses.field(
        default_factory=lambda: {}
    )


# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
class OpalBluetoothDeviceData:
    """Data for Opal BLE sensors."""

    _event: asyncio.Event | None
    _command_data: bytearray | None

    def __init__(
        self,
        logger: Logger,
        elevation: int | None = None,
        is_metric: bool = True,
        voltage: tuple[float, float] = (2.4, 3.2),
    ):
        super().__init__()
        self.logger = logger
        self.is_metric = is_metric
        self.elevation = elevation
        self.voltage = voltage
        
        self._command_data = None
        self._event = None
        self._makeState = None
        self._nightMode = None

    async def _get_status(self, client: BleakClient, device: OpalDevice) -> OpalDevice:
    
        temp = await client.read_gatt_char(MAKE_STATE)
        temp2 = struct.unpack("<B", temp[0:1])[0]
        device.sensors["make_state"] = temp2
        self._makeState = temp2
        
        makeString = ""
        if temp2 == 0:
            makeString = "Off"
        if temp2 == 1:
            makeString = "Making Ice"
        if temp2 == 2:
            makeString = "Out of Water"
        if temp2 == 3:
            makeString = "Bin Full"    
        if temp2 == 4:
            makeString = "Cleaning"
            
        device.sensors["make_state_string"] = makeString
        
        temp = await client.read_gatt_char(ICEBIN_STATE)
        device.sensors["ice_bin_state"] = struct.unpack("<B", temp[0:1])[0]
        
        temp = await client.read_gatt_char(CLEANING_PHASE)
        device.sensors["cleaning_phase"] = struct.unpack("<B", temp[0:1])[0]
        
        temp = await client.read_gatt_char(NIGHT_MODE)
        temp2 = struct.unpack("<B", temp[0:1])[0]
        device.sensors["night_mode"] = temp2
        
        self._nightMode = temp2
        
        return device

    async def night_mode_on(self, ble_device: BLEDevice):
        """Connects to the device through BLE and retrieves relevant data"""

        client = await establish_connection(BleakClient, ble_device, ble_device.address)
        #await client.pair()
        await client.write_gatt_char(NIGHT_MODE,ON_VALUE)
        await client.disconnect()
    
    async def night_mode_off(self, ble_device: BLEDevice):
        """Connects to the device through BLE and retrieves relevant data"""

        client = await establish_connection(BleakClient, ble_device, ble_device.address)
        await client.pair()
        await client.write_gatt_char(NIGHT_MODE,OFF_VALUE)
        await client.disconnect()
    
    async def update_device(self, ble_device: BLEDevice) -> OpalDevice:
        """Connects to the device through BLE and retrieves relevant data"""

        client = await establish_connection(BleakClient, ble_device, ble_device.address)
        await client.pair()
        device = OpalDevice()
        
        
        device = await self._get_status(client, device)
        device.name = ble_device.address
        device.address = ble_device.address
        _LOGGER.debug("device.name: %s", device.name)
        _LOGGER.debug("device.address: %s", device.address)

        await client.disconnect()

        return device
