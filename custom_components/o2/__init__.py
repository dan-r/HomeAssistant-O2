import logging
from .api_client import O2ApiClient
from .coordinator import O2Coordinator
from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config) -> bool:
    return True


async def async_update_listener(hass, entry):
    """Handle options flow credentials update."""
    await hass.data[DOMAIN][DATA_COORDINATOR].async_refresh()


async def async_setup_entry(hass, entry):
    """This is called from the config flow."""
    hass.data.setdefault(DOMAIN, {})

    config = dict(entry.data)

    session = hass.data[DOMAIN][DATA_APICLIENT] = O2ApiClient(
        config.get("email"),
        config.get("password")
    )

    _LOGGER.info("Logging in to service")
    await hass.async_add_executor_job(session.create_session)

    coordinator = hass.data[DOMAIN][DATA_COORDINATOR] = O2Coordinator(hass, config)
 
    _LOGGER.debug("Initialising entities")
    for component in ENTITY_TYPES:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    # Init fetch and state coordinators
    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""

    return await hass.config_entries.async_unload_platforms(entry, ENTITY_TYPES)


async def async_migrate_entry(hass, config_entry) -> bool:
    """Migrate old entry."""
    # Version number has gone backwards
    if CONFIG_VERSION < config_entry.version:
        _LOGGER.error(
            "Backwards migration not possible. Please update the integration.")
        return False

    # Version number has gone up
    if config_entry.version < CONFIG_VERSION:
        _LOGGER.debug("Migrating from version %s", config_entry.version)
        new_data = config_entry.data

        config_entry.version = CONFIG_VERSION
        hass.config_entries.async_update_entry(config_entry, data=new_data)

        _LOGGER.debug("Migration to version %s successful",
                      config_entry.version)

    return True
