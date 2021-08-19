"""Config flow for GreenGo integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from .client.model import City

from .const import *

_LOGGER = logging.getLogger(__name__)

STEP_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_KEY_ZONE_LAT, default=CONF_DEFAULT_ZONE_LAT): cv.latitude,
    vol.Required(CONF_KEY_ZONE_LONG, default=CONF_DEFAULT_ZONE_LONG): cv.longitude,
    vol.Required(CONF_KEY_CITY, default=CONF_DEFAULT_CITY): vol.In(City.list()),
    vol.Required(CONF_KEY_ZONE_RADIUS_KM, default=CONF_DEFAULT_ZONE_RADIUS_KM): vol.All(vol.Coerce(int),
                                                                                        vol.Range(min=1)),
    vol.Required(CONF_KEY_UPDATE_INTERVAL_MIN, default=CONF_DEFAULT_UPDATE_INTERVAL_MIN): vol.All(vol.Coerce(int),
                                                                                                  vol.Range(min=1)),
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> bool:
    """Validate the user input allows us to connect."""

    # Everything is validated in the schema
    return True


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GreenGo."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_DATA_SCHEMA
            )

        errors = {}

        try:
            await validate_input(self.hass, user_input)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=CONF_INTEGRATION_TITLE, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_DATA_SCHEMA, errors=errors
        )

    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry: ConfigEntry):
    #     return OptionsFlowHandler(config_entry)


# class OptionsFlowHandler(config_entries.OptionsFlow):
#
#     def __init__(self, config_entry: ConfigEntry):
#         self.config_entry = config_entry
#
#     async def async_step_init(self, user_input=None):
#         """Manage the options."""
#         if user_input is not None:
#             return self.async_create_entry(title=CONF_INTEGRATION_TITLE, data=user_input)
#
#         # Option schema is same as the config schema, except the default values are the current config values
#         options_schema = vol.Schema({
#             vol.Required(
#                 CONF_KEY_ZONE_LAT,
#                 default=self.config_entry.data.get(CONF_KEY_ZONE_LAT, CONF_DEFAULT_ZONE_LAT)
#             ): cv.latitude,
#             vol.Required(
#                 CONF_KEY_ZONE_LONG,
#                 default=self.config_entry.data.get(CONF_KEY_ZONE_LONG, CONF_DEFAULT_ZONE_LONG)
#             ): cv.longitude,
#             vol.Required(
#                 CONF_KEY_ZONE_RADIUS_KM,
#                 default=self.config_entry.data.get(CONF_KEY_ZONE_RADIUS_KM, CONF_DEFAULT_ZONE_RADIUS_KM)
#             ): vol.All(vol.Coerce(int), vol.Range(min=1)),
#             vol.Required(
#                 CONF_KEY_UPDATE_INTERVAL_MIN,
#                 default=self.config_entry.data.get(CONF_KEY_UPDATE_INTERVAL_MIN, CONF_DEFAULT_UPDATE_INTERVAL_MIN)
#             ): vol.All(vol.Coerce(int), vol.Range(min=1)),
#         })
#
#         return self.async_show_form(
#             step_id="init",
#             data_schema=options_schema,
#         )
