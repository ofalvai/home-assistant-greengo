import math
from typing import Optional

from aiohttp import ClientSession

from .model import Vehicle, City


class GreengoClient:

    def __init__(self, session: ClientSession, city: City):
        self.session = session  # Session is the default HA session, shouldn't be cleaned up
        self.city = city

    async def vehicles_in_zone(self, radius: int, latitude: float, longitude: float) -> list[Vehicle]:
        vehicle_list = await self._fetch_vehicles()

        return [v for v in vehicle_list if self._within_radius(v, radius, latitude, longitude)]

    async def _fetch_vehicles(self) -> list[Vehicle]:
        query_params = {
            "funct": "callAPI",
            "APIname": "getVehicleList"
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"https://greengo.com/{self.city.api_code}/?lang=EN"
        }
        url = f"https://greengo.com/{self.city.api_code}/divcontent.php"
        async with self.session.get(url, params=query_params, headers=headers) as resp:
            resp_json = await resp.json(content_type="text/html")
            return [Vehicle.from_json(item) for item in resp_json]

    def _within_radius(self, vehicle: Vehicle, radius: int, latitude: float, longitude: float) -> bool:
        vehicle_position = (vehicle.latitude, vehicle.longitude)
        vehicle_distance = self._distance(vehicle_position, (latitude, longitude))
        return vehicle_distance <= radius

    @staticmethod
    def nearest(vehicles: list[Vehicle], zone: tuple) -> Optional[Vehicle]:
        sorted_vehicles = sorted(
            vehicles,
            key=lambda v: GreengoClient._distance((v.latitude, v.longitude), zone),
        )
        if sorted_vehicles:
            return sorted_vehicles[0]
        else:
            return None

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
