from .const import *
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the GreenGo sensors from config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_KEY_COORDINATOR]

    async_add_entities([GreengoVehicleCountSensor(coordinator)])


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
