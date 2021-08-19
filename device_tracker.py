import logging
from typing import Optional, Mapping, Any

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import LENGTH_KILOMETERS
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import EntityPlatform
from homeassistant.helpers.entity_registry import EntityRegistry, async_get as async_get_entity_registry
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .client import Vehicle
from .client.model import VehicleID
from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the GreenGo tracker from config entry."""

    _LOGGER.debug("Setting up device_tracker with config data: %s", config_entry.data)

    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_KEY_COORDINATOR]
    entity_manager = GreengoEntityManager(
        async_add_entities,
        coordinator,
        async_get_entity_registry(hass),
        entity_platform.async_get_current_platform()
    )

    @callback
    def update_entities():
        hass.async_create_task(entity_manager.update_entities())

    coordinator.async_add_listener(update_entities)

    async_add_entities(
        GreengoTrackerEntity(coordinator, vehicle_id) for vehicle_id in coordinator.data.keys()
    )


class GreengoEntityManager:
    def __init__(self, async_add_entities, coordinator, entity_registry: EntityRegistry, platform: EntityPlatform):
        self.async_add_entities = async_add_entities
        self.coordinator = coordinator
        self.entity_registry = entity_registry
        self.platform = platform
        self.vehicles: dict[VehicleID, Vehicle] = {}

    async def update_entities(self):
        new_vehicles = self.coordinator.data

        to_add = set(new_vehicles) - set(self.vehicles)  # Diff of vehicle IDs
        to_remove = set(self.vehicles) - set(new_vehicles)  # Diff of vehicle IDs

        await self._add_entities(to_add)
        await self._remove_entities(to_remove)
        self.vehicles = new_vehicles

    async def _add_entities(self, to_add: set[VehicleID]):
        if to_add and self.vehicles:
            _LOGGER.debug("Adding %d new vehicles after update: %s", len(to_add), to_add)

            self.async_add_entities(
                GreengoTrackerEntity(self.coordinator, vehicle_id) for vehicle_id in to_add
            )

    async def _remove_entities(self, to_remove: set[VehicleID]):
        for vehicle_id in to_remove:
            plate_number = self.vehicles[vehicle_id].plate_number
            entity_id = f"device_tracker.greengo_{plate_number.lower()}"
            _LOGGER.debug("Removing entity %s (id=%s) because it's missing from API response.", plate_number, entity_id)

            if self.entity_registry.async_get(entity_id):
                await self.platform.async_remove_entity(entity_id)
                self.entity_registry.async_remove(entity_id)


class GreengoTrackerEntity(CoordinatorEntity, TrackerEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, vehicle_id: VehicleID):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.vehicle_id: VehicleID = vehicle_id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            _ = self._vehicle()
            self.async_write_ha_state()  # Continue with update
        except KeyError:
            # Vehicle is missing from API response, but it's okay. GreenGoEntityManager will be notified and it
            # will remove the entity completely
            pass

    @property
    def unique_id(self):
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return UNIQUE_ID_TRACKER.format(self.vehicle_id)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'GreenGo ' + self._vehicle().plate_number

    @property
    def state(self) -> StateType:
        """Return the remaining range (in kilometers) of the vehicle."""
        return self._vehicle().estimated_km

    @property
    def unit_of_measurement(self) -> Optional[str]:
        return LENGTH_KILOMETERS

    @property
    def latitude(self) -> float:
        """The latitude coordinate of the vehicle."""
        return self._vehicle().latitude

    @property
    def longitude(self) -> float:
        """	The longitude coordinate of the vehicle."""
        return self._vehicle().longitude

    @property
    def source_type(self):
        return SOURCE_TYPE_GPS

    @property
    def icon(self):
        return "mdi:car"

    @property
    def extra_state_attributes(self) -> Optional[Mapping[str, Any]]:
        return {
            "Estimated range (km)": self.state,
            "Plate number": self._vehicle().plate_number,
            "Address": self.location_name
        }

    @property
    def entity_picture(self) -> Optional[str]:
        original_url = self._vehicle().icon_url
        return original_url.replace("mapicons/v2/32/", "mapicons/v2/64/")

    @property
    def battery_level(self):
        return self._vehicle().battery_level

    @property
    def location_name(self) -> str:
        return self._vehicle().address

    def _vehicle(self) -> Vehicle:
        return self.coordinator.data[self.vehicle_id]
