from datetime import timedelta
from typing import Optional, Mapping, Any

import async_timeout
import logging

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.const import LENGTH_KILOMETERS
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed
from .client import GreengoClient
from .const import *



class ApiError(Exception):
    pass


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the GreenGo tracker from config entry."""

    _LOGGER.debug("Setting up device_tracker with config data: %s", config_entry.data)

    session = async_get_clientsession(hass)
    client = GreengoClient(session)

    update_interval_min = config_entry.data[CONF_KEY_UPDATE_INTERVAL_MIN]
    radius = config_entry.data[CONF_KEY_ZONE_RADIUS_KM]
    latitude = config_entry.data[CONF_KEY_ZONE_LAT]
    longitude = config_entry.data[CONF_KEY_ZONE_LONG]

    async def async_update_data():
        try:
            async with async_timeout.timeout(10):
                vehicle_map = await data_handler.update_vehicles(radius, latitude, longitude)
                return vehicle_map
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="GreenGo API",
        update_method=async_update_data,
        update_interval=timedelta(minutes=update_interval_min),
    )

    data_handler = GreengoDataHandler(client, async_add_entities, coordinator)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        GreengoSensor(coordinator, vehicle_id) for vehicle_id in coordinator.data.keys()
    )


class GreengoDataHandler:
    def __init__(self, client: GreengoClient, async_add_entities, coordinator):
        self.client = client
        self.async_add_entities = async_add_entities
        self.coordinator = coordinator
        self.vehicles: dict = {}

    async def update_vehicles(self, radius: int, latitude: float, longitude: float) -> dict:
        vehicle_list = await self.client.vehicles_in_zone(radius, latitude, longitude)
        _LOGGER.debug("Fetched %d vehicles from API", len(vehicle_list))
        new_vehicles = {v["vehicle_id"]: v for v in vehicle_list}

        to_add = set(new_vehicles) - set(self.vehicles)  # Diff of vehicle IDs
        if to_add and self.vehicles:
            _LOGGER.debug("Adding %d new vehicles after update: %s", len(to_add), to_add)

            self.async_add_entities(
                GreengoSensor(self.coordinator, vehicle_id) for vehicle_id in to_add
            )

        self.vehicles = new_vehicles

        return self.vehicles




class GreengoSensor(CoordinatorEntity, TrackerEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, vehicle_id: str):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.vehicle_id = vehicle_id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            _ = self._vehicle()
            self.async_write_ha_state()  # Continue with update
        except KeyError:
            _LOGGER.debug("Vehicle %s is missing from API response. Removing its entity.", self.vehicle_id)
            self._remove()

    @property
    def unique_id(self):
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return UNIQUE_ID_TEMPLATE.format(self.vehicle_id)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'GreenGo ' + self._vehicle()["plate_number"]

    @property
    def state(self) -> StateType:
        """Return the remaining range (in kilometers) of the vehicle."""
        return int(self._vehicle()["estimated_km"])

    @property
    def unit_of_measurement(self) -> Optional[str]:
        return LENGTH_KILOMETERS

    @property
    def latitude(self) -> float:
        """The latitude coordinate of the car."""
        return float(self._vehicle()["gps_lat"])

    @property
    def longitude(self) -> float:
        """	The longitude coordinate of the car."""
        return float(self._vehicle()["gps_long"])

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:car"

    @property
    def extra_state_attributes(self) -> Optional[Mapping[str, Any]]:
        return {
            "Estimated range": self.state,
            "Plate number": self._vehicle()["plate_number"],
            "Address": self.location_name
        }

    @property
    def entity_picture(self) -> Optional[str]:
        original_url: str = self._vehicle()["icon"]
        return original_url.replace("mapicons/v2/32/", "mapicons/v2/64/")

    @property
    def battery_level(self):
        return self._vehicle()["battery_level"]

    @property
    def location_name(self) -> str:
        return self._vehicle()["address"]

    def _vehicle(self) -> dict:
        return self.coordinator.data[self.vehicle_id]

    def _remove(self):
        """Remove entity itself."""

        self.hass.async_create_task(self.async_remove(force_remove=True))

