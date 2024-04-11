import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity
)
from homeassistant.core import callback
from homeassistant.const import PERCENTAGE, UnitOfInformation
from .coordinator import O2Coordinator
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR, DATA_APICLIENT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config, async_add_entities):
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][DATA_COORDINATOR]
    client = hass.data[DOMAIN][DATA_APICLIENT]

    if client.number is None:
        raise Exception("Fetching plan information failed")

    entities = [DataSensor(coordinator, hass)]

    async_add_entities(entities, update_before_add=True)


class DataSensor(CoordinatorEntity[O2Coordinator], SensorEntity):
    _attr_name = "Data Remaining"
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.DATA_SIZE
    _attr_native_unit_of_measurement = UnitOfInformation.GIGABYTES
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator, hass):
        super().__init__(coordinator=coordinator)

        self._client = hass.data[DOMAIN][DATA_APICLIENT]
        self._attributes = {}
        self._last_updated = None
        self._state = None

        self.entity_id = generate_entity_id(
            "sensor.{}", f"o2_{self._client.number}_data_remaining", hass=hass)

        self._attr_device_info = self._client.get_device_info()

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.entity_id

    @property
    def native_value(self):
        """Get value from data returned from API by coordinator"""
        if self.coordinator.data:
            return self.coordinator.data['allowancesBalance']['data'][0]['balance'] / 1024
        
        return None

    @property
    def icon(self):
        """Icon of the sensor."""
        return "mdi:chart-donut"
