"""Constants for the GreenGo integration."""

DOMAIN = "greengo"
PLATFORMS = ["device_tracker"]

CONF_INTEGRATION_TITLE = "GreenGo"

CONF_KEY_ZONE_RADIUS_KM = "zone_radius"
CONF_KEY_ZONE_LAT = "zone_lat"
CONF_KEY_ZONE_LONG = "zone_long"
CONF_KEY_UPDATE_INTERVAL_MIN = "update_interval"

CONF_DEFAULT_ZONE_LAT = 47.4979
CONF_DEFAULT_ZONE_LONG = 19.0402
CONF_DEFAULT_ZONE_RADIUS_KM = 1
CONF_DEFAULT_UPDATE_INTERVAL_MIN = 5

UNIQUE_ID_TEMPLATE = "greengo_vehicle_{0}"
