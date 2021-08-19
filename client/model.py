from dataclasses import dataclass
from enum import Enum


class City(Enum):
    BUDAPEST = ("Budapest", "hu")
    PRAGUE = ("Prague", "cz")

    def __init__(self, label: str, api_code: str):
        self.label = label
        self.api_code = api_code

    @classmethod
    def list(cls) -> list[str]:
        return [c.label for c in City]

    @classmethod
    def get_by_label(cls, label: str):
        for city in cls:
            if city.label == label:
                return city
        raise ValueError


VehicleID = int


@dataclass
class Vehicle:
    vehicle_id: VehicleID
    plate_number: str
    latitude: float
    longitude: float
    address: str
    battery_level: float
    estimated_km: int
    icon_url: str

    @classmethod
    def from_json(cls, json):
        return cls(
            vehicle_id=int(json["vehicle_id"]),
            plate_number=json["plate_number"],
            latitude=float(json["gps_lat"]),
            longitude=float(json["gps_long"]),
            address=json["address"],
            battery_level=float(json["battery_level"]),
            estimated_km=int(json["estimated_km"]),
            icon_url=json["icon"]
        )
