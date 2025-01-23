from dataclasses import dataclass
import math

from .primitives import Angle, AngularSpeed, Au, AuSpeed
from .zodiac import Zodiac, ZodiacConstell


@dataclass
class EclCoord:
    """Ecliptic coordinate"""

    latitude: Angle
    longitude: Angle
    distance: Au

    def __init__(self, longitude: float, latitude: float, distance: float):
        self.longitude = Angle(longitude)
        self.latitude = Angle(latitude)
        self.distance = Au(distance)

    def __eq__(self, other) -> bool:
        return self.latitude == other.latitude and self.longitude == other.longitude

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
            ang = 2.0 * math.pi - ang
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

    def json(self) -> dict:
        return {'lat': self.latitude.degrees, 'long': self.longitude.degrees, 'dist': self.distance.au}


@dataclass
class EquatorCoord:
    """Equatorial coordinate"""

    ra: Angle
    decl: Angle
    distance: Au

    def __init__(self, ra: float, decl: float, distance: float):
        self.ra = Angle(ra)
        self.decl = Angle(decl)
        self.distance = Au(distance)

    def json(self) -> dict:
        return {'ra': self.ra.degrees, 'decl': self.decl.degrees, 'dist': self.distance.au}

@dataclass
class BaryCoord:
    """Barycentric coordinate"""

    latitude: Angle
    longitude: Angle
    distance: Au

    def __init__(self, longitude: float, latitude: float, distance: float):
        self.longitude = Angle(longitude)
        self.latitude = Angle(latitude)
        self.distance = Au(distance)

    def json(self) -> dict:
        return {'lat': self.latitude.degrees, 'long': self.longitude.degrees, 'dist': self.distance.au}

@dataclass
class HelioCoord:
    """Heliocentric coordinate"""

    latitude: Angle
    longitude: Angle
    distance: Au

    def __init__(self, longitude: float, latitude: float, distance: float):
        self.longitude = Angle(longitude)
        self.latitude = Angle(latitude)
        self.distance = Au(distance)

    def json(self) -> dict:
        return {'lat': self.latitude.degrees, 'long': self.longitude.degrees, 'dist': self.distance.au}


@dataclass
class HorCoord:
    """Horizontal coordinate"""

    azimuth: Angle
    altitude: Angle
    distance: Au

    def __init__(self, azimuth: float, altitude: float, distance: float):
        self.azimuth = Angle(azimuth)
        self.altitude = Angle(altitude)
        self.distance = Au(distance)

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

    def json(self) -> dict:
        return {'azimuth': self.azimuth.degrees, 'alt': self.altitude.degrees, 'dist': self.distance.au}


@dataclass
class EclSpeed(EclCoord):
    """Ecliptic coordinate with speed"""

    longitude_speed: AngularSpeed
    latitude_speed: AngularSpeed
    distance_speed: AuSpeed

    def __init__(self, longitude: float, latitude: float, dist: float, longitude_speed: float, latitude_speed: float, distance_speed: float):
        super().__init__(longitude, latitude, dist)
        self.longitude_speed = AngularSpeed(longitude_speed)
        self.latitude_speed = AngularSpeed(latitude_speed)
        self.distance_speed = AuSpeed(distance_speed)

    def json(self) -> dict:
        d = super().json()
        d['long_spd'] = self.longitude_speed.deg_per_day
        d['lat_spd'] = self.latitude_speed.deg_per_day
        d['dist_spd'] = self.distance_speed.au_per_day
        return d

@dataclass
class EquatorSpeed(EquatorCoord):
    """Ecliptic coordinate with speed"""

    ra_speed: AngularSpeed
    decl_speed: AngularSpeed
    distance_speed: AuSpeed

    def __init__(self, ra: float, decl: float, dist: float, ra_speed: float, decl_speed: float, distance_speed: float):
        super().__init__(ra, decl, dist)
        self.ra_speed = AngularSpeed(ra_speed)
        self.decl_speed = AngularSpeed(decl_speed)
        self.distance_speed = AuSpeed(distance_speed)

    def json(self) -> dict:
        d = super().json()
        d['ra_spd'] = self.ra_speed.deg_per_day
        d['decl_spd'] = self.decl_speed.deg_per_day
        d['dist_spd'] = self.distance_speed.au_per_day
        return d

@dataclass
class BarySpeed(BaryCoord):
    """Barycentric coordinate with speed"""

    longitude_speed: AngularSpeed
    latitude_speed: AngularSpeed
    distance_speed: AuSpeed

    def __init__(self, longitude: float, latitude: float, dist: float, longitude_speed: float, latitude_speed: float, distance_speed: float):
        super().__init__(longitude, latitude, dist)
        self.longitude_speed = AngularSpeed(longitude_speed)
        self.latitude_speed = AngularSpeed(latitude_speed)
        self.distance_speed = AuSpeed(distance_speed)

    def json(self) -> dict:
        d = super().json()
        d['long_spd'] = self.longitude_speed.deg_per_day
        d['lat_spd'] = self.latitude_speed.deg_per_day
        d['dist_spd'] = self.distance_speed.au_per_day
        return d

@dataclass
class HelioSpeed(HelioCoord):
    """Heliocentric coordinate with speed"""

    longitude_speed: AngularSpeed
    latitude_speed: AngularSpeed
    distance_speed: AuSpeed

    def __init__(self, longitude: float, latitude: float, dist: float, longitude_speed: float, latitude_speed: float, distance_speed: float):
        super().__init__(longitude, latitude, dist)
        self.longitude_speed = AngularSpeed(longitude_speed)
        self.latitude_speed = AngularSpeed(latitude_speed)
        self.distance_speed = AuSpeed(distance_speed)

    def json(self) -> dict:
        d = super().json()
        d['long_spd'] = self.longitude_speed.deg_per_day
        d['lat_spd'] = self.latitude_speed.deg_per_day
        d['dist_spd'] = self.distance_speed.au_per_day
        return d
