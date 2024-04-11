import logging

from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, DATA_APICLIENT

_LOGGER = logging.getLogger(__name__)


class O2Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        """Coordinator to fetch the latest states."""
        super().__init__(
            hass,
            _LOGGER,
            name="Update Coordinator",
            update_interval=timedelta(minutes=30),
        )
        self._hass = hass

    async def _async_update_data(self):
        """Fetch data from API."""
        client = self._hass.data[DOMAIN][DATA_APICLIENT]
        
        try:
            data = await self._hass.async_add_executor_job(client.get_allowances)
            return data
        except BaseException:
            _LOGGER.warning("Error communicating with API")
            return False
