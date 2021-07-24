from typing import Optional, Mapping, Any

from . import GreengoClient
from .const import *
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the GreenGo sensors from config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_KEY_COORDINATOR]
    zone_lat = config_entry.data[CONF_KEY_ZONE_LAT]
    zone_long = config_entry.data[CONF_KEY_ZONE_LONG]

    async_add_entities([
        GreengoVehicleCountSensor(coordinator),
        GreengoClosestVehicleSensor(coordinator, zone_lat, zone_long)
    ])


class GreengoVehicleCountSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

    @property
    def name(self) -> str:
        return "GreenGo vehicles in zone"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_SENSOR_VEHICLE_COUNT

    @property
    def state(self) -> int:
        return len(self.coordinator.data.keys())

    @property
    def unit_of_measurement(self) -> str:
        return "vehicles"

    @property
    def icon(self) -> str:
        return "mdi:car"


class GreengoClosestVehicleSensor(CoordinatorEntity, SensorEntity):
    """Closest vehicle to the configured lat/long pair."""

    def __init__(self, coordinator, zone_lat: float, zone_long: float):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.zone_lat = zone_lat
        self.zone_long = zone_long

    def _vehicle(self):
        vehicles = list(self.coordinator.data.values())  # Dict of [id -> vehicle] turned to vehicle list
        return GreengoClient.nearest(vehicles, (self.zone_lat, self.zone_long))
        # TODO: handle null case

    @property
    def name(self) -> str:
        return "Closest GreenGo vehicle"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_SENSOR_CLOSEST

    @property
    def state(self) -> int:
        return self._vehicle()["plate_number"]

    @property
    def icon(self) -> str:
        return "mdi:car"

    @property
    def extra_state_attributes(self) -> Optional[Mapping[str, Any]]:
        return {
            "Plate number": self._vehicle()["plate_number"],
            "Estimated range (km)": self._vehicle()["estimated_km"],
            "Battery level": self._vehicle()["battery_level"],
            "Address": self._vehicle()["address"],
            "Latitude": float(self._vehicle()["gps_lat"]),
            "Longitude": float(self._vehicle()["gps_long"]),
        }

    @property
    def entity_picture(self) -> Optional[str]:
        original_url: str = self._vehicle()["icon"]
        return original_url.replace("mapicons/v2/32/", "mapicons/v2/64/")
