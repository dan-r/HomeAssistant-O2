import voluptuous as vol
from homeassistant.config_entries import (ConfigFlow, OptionsFlow)
from .const import DOMAIN, CONFIG_VERSION
from .api_client import O2ApiClient
import homeassistant.helpers.config_validation as cv
import logging

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema({
    vol.Required("email"): cv.string,
    vol.Required("password"): cv.string
})


class O2ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow."""
    VERSION = CONFIG_VERSION

    async def async_step_user(self, info):
        errors = {}
        if info is not None:
            # Validate credentials
            session = O2ApiClient(
                info["email"],
                info["password"]
            )

            try:
                await self.hass.async_add_executor_job(session.create_session)
            except:
                errors["base"] = "auth_error"

            if len(errors) == 0:
                return self.async_create_entry(
                    title=info['email'],
                    data=info
                )

        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )

    def async_get_options_flow(entry):
        return O2OptionsFlow(entry)


class O2OptionsFlow(OptionsFlow):
    """Options flow."""

    def __init__(self, entry) -> None:
        self._config_entry = entry

    async def async_step_init(self, options):
        errors = {}
        # If form filled
        if options is not None:
            data = dict(self._config_entry.data)
            # Validate credentials
            if "password" in options:
                session = O2ApiClient(
                    options["email"],
                    options["password"]
                )
                try:
                    await self.hass.async_add_executor_job(session.create_session)
                except:
                    errors["base"] = "auth_error"

            # If we have no errors, update the data array
            if len(errors) == 0:
                # If password not provided, dont take the new details
                if not "password" in options:
                    options.pop('email', None)
                    options.pop('password', None)
                
                # Update data
                data.update(options)
                self.hass.config_entries.async_update_entry(
                    self._config_entry, data=data, title=data['email']
                )

                # Update options
                return self.async_create_entry(
                    title="",
                    data={}
                )

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema({
                vol.Required("email", default=self._config_entry.data.get("email", "")): cv.string,
                vol.Optional("password"): cv.string
            }), errors=errors
        )
