"""The GreenGo integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .client import GreengoClient, Vehicle
from .client.model import VehicleID, City
from .const import *
from .device_tracker import GreengoTrackerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up GreenGo from a config entry."""

    update_interval_min = config_entry.data[CONF_KEY_UPDATE_INTERVAL_MIN]
    radius = config_entry.data[CONF_KEY_ZONE_RADIUS_KM]
    latitude = config_entry.data[CONF_KEY_ZONE_LAT]
    longitude = config_entry.data[CONF_KEY_ZONE_LONG]
    city = City.get_by_label(config_entry.data.get(CONF_KEY_CITY, CONF_DEFAULT_CITY))

    session = async_get_clientsession(hass)
    client = GreengoClient(session, city)

    async def update_vehicles() -> dict[VehicleID, Vehicle]:
        try:
            async with async_timeout.timeout(10):
                vehicle_list = await client.vehicles_in_zone(radius, latitude, longitude)
                _LOGGER.debug("Fetched %d vehicles from API", len(vehicle_list))
                return {v.vehicle_id: v for v in vehicle_list}
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_interval=timedelta(minutes=update_interval_min),
        update_method=update_vehicles,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = {
        DATA_KEY_COORDINATOR: coordinator
    }

    hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

    # entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        del hass.data[DOMAIN]

    return unload_ok

# async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
#     """Handle options update."""
#     await hass.config_entries.async_reload(entry.entry_id)
