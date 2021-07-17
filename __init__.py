"""The GreenGo integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .device_tracker import GreengoSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GreenGo from a config entry."""

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    # entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok


# async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
#     """Handle options update."""
#     await hass.config_entries.async_reload(entry.entry_id)
