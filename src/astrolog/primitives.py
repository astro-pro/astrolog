from dataclasses import dataclass
from types import NoneType

from dms2dec.dms_convert import dms2dec
import math

@dataclass
class Au:
    """Distance in astronomic units (a.u.)"""

    def __init__(self, au: float):
        self.au = au

@dataclass
class AuSpeed:
    """Speed in astronomic units (a.u.) per day"""

    def __init__(self, speed: float):
        self.au_per_day = speed

@dataclass
class Angle:
    """Angle measured in degrees"""

    def __init__(self, degrees: str | float | int | NoneType = None, *, radians: float | int | NoneType = None):
        if radians is not None and degrees is not None:
            raise RuntimeError("either degrees or radians has to be provided to the method")
        elif degrees is not None:
            if type(degrees) is str:
                self.degrees = dms2dec(degrees)
            elif type(degrees) is float or type(degrees) is int:
                self.degrees = degrees
        elif radians is not None:
            self.degrees = radians * 180.0 / math.pi

    def __eq__(self, other) -> bool:
        return self.degrees == other.degrees

    def radians(self):
        return self.degrees * 2.0 * math.pi / 360.0

    def aspect(self, orb: float = 0.5):
        if -orb <= self.degrees <= orb:
            return 1
        for div in range(2, 14):
            angle = 360.0 / div
            if angle - orb <= self.degrees <= angle + orb:
                return div
        return None


@dataclass
class AngularSpeed:
    """Angular speed measured in degrees per day"""
    def __init__(self, speed: float | int):
        self.deg_per_day = speed


@dataclass
class GeoLocation:
    """Location on the earth"""

    def __init__(self, longitude, latitude):
        self.longitude = Angle(longitude)
        self.latitude = Angle(latitude)
