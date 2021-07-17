import json
import math

from aiohttp import ClientSession

BASE_URL = "https://greengo.com/hu/divcontent.php"


class GreengoClient:

    def __init__(self, session: ClientSession):
        self.session = session  # Session is the default HA session, shouldn't be cleaned up

    async def vehicles_in_zone(self, radius: int, latitude: float, longitude: float) -> list:
        vehicle_list = await self._fetch_vehicles()

        return [v for v in vehicle_list if self._within_radius(v, radius, latitude, longitude)]

    async def _fetch_vehicles(self) -> list:
        query_params = {
            "funct": "callAPI",
            "APIname": "getVehicleList"
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://greengo.com/hu/?lang=HU"
        }
        async with self.session.get(BASE_URL, params=query_params, headers=headers) as resp:
            resp_data = await resp.read()
            # Content type is incorrectly set to text/html, so we parse manually to avoid warning
            resp_json = json.loads(resp_data)
            return resp_json

    def _within_radius(self, vehicle, radius: int, latitude: float, longitude: float) -> bool:
        vehicle_position = (float(vehicle["gps_lat"]), float(vehicle["gps_long"]))
        vehicle_distance = self._distance(vehicle_position, (latitude, longitude))
        return vehicle_distance <= radius

    @staticmethod
    def _distance(origin: tuple, destination: tuple) -> float:
        """Calculate the Haversine distance."""

        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = 6371  # km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c

        return d
