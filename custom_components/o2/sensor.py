import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfInformation
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, DATA_COORDINATOR, DATA_APICLIENT
from datetime import datetime

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config, async_add_entities):
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][DATA_COORDINATOR]
    client = hass.data[DOMAIN][DATA_APICLIENT]

    if client.number is None:
        raise Exception("Fetching plan information failed")

    entities = [
        O2AllowanceSensor(coordinator, hass, "Data Remaining", "data", UnitOfInformation.GIGABYTES, "mdi:chart-donut"),
        O2AllowanceSensor(coordinator, hass, "Texts Remaining", "text", None, "mdi:message"),
        O2AllowanceSensor(coordinator, hass, "Minutes Remaining", "voice", None, "mdi:phone"),
        O2AllowanceResetSensor(coordinator, hass)
    ]

    async_add_entities(entities, update_before_add=True)


class O2AllowanceSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, hass, name, data_type, unit_of_measurement, icon):
        super().__init__(coordinator=coordinator)

        self._client = hass.data[DOMAIN][DATA_APICLIENT]
        self._attr_name = name
        self._data_type = data_type
        self._unit_of_measurement = unit_of_measurement
        self._icon = icon

        self.entity_id = generate_entity_id(
            "sensor.{}", f"o2_{self._client.number}_{self._attr_name.lower().replace(' ', '_')}", hass=hass)

        self._attr_device_info = self._client.get_device_info()

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.entity_id

    @property
    def native_value(self):
        """Get value from data returned from API by coordinator"""
        if self.coordinator.data:
            remaining = self.coordinator.data['allowancesBalance'][self._data_type][0]
            if 'balance' in remaining:
                if self._unit_of_measurement == UnitOfInformation.GIGABYTES:
                    return remaining['balance'] / 1024
                else:
                    return remaining['balance']
            else:
                return 'Unlimited'
        
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement
    
    @property
    def suggested_display_precision(self):
        if self._unit_of_measurement == UnitOfInformation.GIGABYTES:
            return 2
        return None

    @property
    def icon(self):
        """Icon of the sensor."""
        return self._icon

class O2AllowanceResetSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_name = "Allowance Reset Date"

    def __init__(self, coordinator, hass):
        super().__init__(coordinator=coordinator)

        self._client = hass.data[DOMAIN][DATA_APICLIENT]

        self.entity_id = generate_entity_id(
            "sensor.{}", f"o2_{self._client.number}_{self._attr_name.lower().replace(' ', '_')}", hass=hass)

        self._attr_device_info = self._client.get_device_info()

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.entity_id

    @property
    def state(self):
        """Return the state."""
        if self.coordinator.data:
            expiresDate = self.coordinator.data['allowancesBalance']['data'][0]['details'][0]['expiresDate']
            date_obj = datetime.strptime(expiresDate, '%d %B %Y')
            
            return date_obj.isoformat()
        
        return None
    
    @property
    def icon(self):
        """Icon of the sensor."""
        return "mdi:calendar-range"
