from dataclasses import dataclass
import math

from .primitives import Angle
from .zodiac import Zodiac, ZodiacConstell

@dataclass
class EclCoord:
    """Ecliptic coordinate"""

    latitude: Angle
    longitude: Angle

    def __init__(self, longitude: float, latitude: float):
        self.longitude = Angle(longitude)
        self.latitude = Angle(latitude)

    def __xor__(self, other) -> Angle:
        if self == other:
            return Angle(0)
        long1 = self.longitude.radians()
        long2 = other.longitude.radians()
        lat1 = self.latitude.radians()
        lat2 = other.latitude.radians()
        dalpha = long1 - long2
        cosd = math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(dalpha)
        ang = math.acos(cosd)
        if ang > math.pi:
            ang = 2 * math.pi - ang
        return Angle(radians=ang)

    def sign_pos(self) -> (Zodiac, float):
        sign = Zodiac.from_longitude(self.longitude)
        return sign, self.longitude.degrees - sign.offset

    def constell_pos(self) -> (ZodiacConstell, float):
        constell = ZodiacConstell.from_longitude(self.longitude)
        pos = self.longitude.degrees
        if constell.upto_lng < constell.from_lng < pos:
            offset = pos - constell.from_lng
        elif pos < constell.upto_lng < constell.from_lng:
            offset = pos
        else:
            offset = pos - constell.from_lng
        return constell, offset


@dataclass
class EquatorCoord:
    """Equatorial coordinate"""

    ra: Angle
    decl: Angle

    def __init__(self, ra: float, decl: float):
        self.ra = Angle(ra)
        self.decl = Angle(decl)


@dataclass
class HorCoord:
    """Horizontal coordinate"""

    azimuth: Angle
    altitude: Angle

    def __init__(self, azimuth: float, altitude: float):
        self.azimuth = Angle(azimuth)
        self.altitude = Angle(altitude)

    def house_pos(self) -> (int, float):
        alt = self.altitude.radians()
        azimuth = self.azimuth.radians()
        angle = math.atan2(math.tan(alt), math.cos(azimuth)) / math.pi * 180.0 - 90.0
        if angle < 0:
            angle += 360
        house13 = int(math.floor(angle * 13.0 / 360.0)) + 1
        house_pos = angle * 13.0 / 360.0 + 1.0 - house13
        house_pos *= 180.0 / math.pi
        return house13, house_pos
