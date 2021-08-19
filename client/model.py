from dataclasses import dataclass

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
