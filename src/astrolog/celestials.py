from abc import ABC, abstractmethod
from datetime import datetime, time, timedelta
from types import NoneType

import swisseph as swe

from . import GeoLocation, EclCoord, EquatorCoord, HorCoord
from .coords import EclSpeed, EquatorSpeed


class Celestial(ABC):
    """Abstract class for celestial objects whose location can be computed"""

    NAMES = {
        "SUN": swe.SUN,
        "MOON": swe.MOON,
        "MERCURY": swe.MERCURY,
        "VENUS": swe.VENUS,
        "MARS": swe.MARS,
        "EARTH": swe.EARTH,
        "JUPITER": swe.JUPITER,
        "SATURN": swe.SATURN,
        "URANUS": swe.URANUS,
        "NEPTUNE": swe.NEPTUNE,
        "PLUTO": swe.PLUTO,
        "ERIS": swe.AST_OFFSET + 136199,
        "SEDNA": swe.AST_OFFSET + 90377,
        "QUAOAR": swe.AST_OFFSET + 50000,
    }

    def __init__(self):
        self.name = None

    def ecl_coord(self, time: datetime, location: GeoLocation, *, speed: bool = False, mean: bool = False) -> EclCoord | EclSpeed:
        swe.set_topo(location.longitude.degrees, location.latitude.degrees)
        jd = swe.julday(time.year, time.month, time.day, time.hour + time.minute / 60.)
        return self.swe_ecl_coord(jd, speed=speed, mean=mean)

    def equator_coord(self, time: datetime, location: GeoLocation, *, speed: bool = False, mean: bool = False) -> EquatorCoord | EquatorSpeed:
        swe.set_topo(location.longitude.degrees, location.latitude.degrees)
        jd = swe.julday(time.year, time.month, time.day, time.hour + time.minute / 60.)
        return self.swe_equator_coord(jd, speed=speed, mean=mean)

    def hor_coord(self, time: datetime, location: GeoLocation, *, mean: bool = False) -> HorCoord:
        swe.set_topo(location.longitude.degrees, location.latitude.degrees)
        jd = swe.julday(time.year, time.month, time.day, time.hour + time.minute / 60.)
        coord = self.swe_equator_coord(jd, mean=mean)
        geopos = (location.longitude.degrees, location.latitude.degrees, 0.0)
        pos = (coord.ra.degrees, coord.decl.degrees, 0.0)
        atpress = 0
        attemp = 0
        (azimuth, true_alt, app_alt) = swe.azalt(jd, swe.EQU2HOR, geopos, atpress, attemp, pos)
        return HorCoord(azimuth, true_alt)

    def ecl_speed(self, time: datetime, location: GeoLocation, **kwargs) -> EclSpeed:
        return self.ecl_coord(time, location, speed=True, **kwargs)

    def equator_speed(self, time: datetime, location: GeoLocation, **kwargs) -> EquatorSpeed:
        return self.equator_coord(time, location, speed=True, **kwargs)

    def transits(self, time: datetime, location: GeoLocation):
        return {
            'rise': self.rises(time, location),
            'set': self.sets(time, location),
            'mc': self.mc_trans(time, location),
            'ic': self.ic_trans(time, location),
        }

    def rises(self, time: datetime, location: GeoLocation):
        return self.__rise_trans(time, location, swe.CALC_RISE)

    def sets(self, time: datetime, location: GeoLocation):
        return self.__rise_trans(time, location, swe.CALC_SET)

    def mc_trans(self, time: datetime, location: GeoLocation):
        return self.__rise_trans(time, location, swe.CALC_MTRANSIT)

    def ic_trans(self, time: datetime, location: GeoLocation):
        return self.__rise_trans(time, location, swe.CALC_ITRANSIT)

    def __rise_trans(self, when: datetime, location: GeoLocation, rsmi: int):
        if self.is_focal_point():
            return None
        tjdut = swe.julday(when.year, when.month, when.day, 0.)
        flags = swe.FLG_SWIEPH | swe.FLG_TOPOCTR
        rsmi |= swe.BIT_DISC_CENTER | swe.BIT_FIXED_DISC_SIZE | swe.BIT_NO_REFRACTION | swe.BIT_ASTRO_TWILIGHT
        lon = location.longitude.degrees
        lat = location.latitude.degrees
        alt = 0.0
        atpress = 0
        attemp = 0
        (found, (jultime, _, _, _, _, _, _, _, _, _)) = swe.rise_trans(
            tjdut, self.swe_id(), rsmi, (lon, lat, alt), atpress, attemp, flags
        )
        if found != 0:
            return None
        (year, month, day, tm) = swe.revjul(jultime)
        if year != when.year or month != when.month or day != when.day:
            return None
        hours = int(tm)
        minutes = (tm - hours) * 60.
        seconds = (tm - hours - int(minutes) / 60) * 60 * 60
        return timedelta(hours=hours, minutes=int(minutes), seconds=int(seconds))

    @abstractmethod
    def swe_id(self):
        pass

    @classmethod
    def swe_id_by_name(cls, name: str) -> int:
        swe_code = cls.NAMES.get(name.upper())
        if swe_code is None:
            raise Exception(f"Unknown planet {name}")
        return swe_code

    @abstractmethod
    def is_fixed(self) -> bool:
        pass

    @abstractmethod
    def is_focal_point(self) -> bool:
        pass

    @abstractmethod
    def swe_ecl_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EclCoord | EclSpeed:
        pass

    @abstractmethod
    def swe_equator_coord(self, jd, speed: bool = False, mean: bool = False) -> EquatorCoord | EclSpeed:
        pass


class Planet(Celestial):
    """Planets (moving physical bodies)"""

    def __init__(self, name: str, swe_code: int | NoneType = None):
        self.name = name
        self.__swe_code = swe_code or Celestial.swe_id_by_name(name)

    def is_fixed(self) -> bool:
        return False

    def is_focal_point(self) -> bool:
        return False

    def swe_id(self):
        return self.__swe_code

    def swe_ecl_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EclCoord | EclSpeed:
        if mean is not False:
            raise RuntimeError("mean position flag has no meaning for the planets")
        iflag = swe.FLG_SWIEPH | swe.FLG_TOPOCTR
        if speed:
            iflag |= swe.FLG_SPEED
        (ecl, _) = swe.calc_ut(jd, self.__swe_code, iflag)
        if speed:
            return EclSpeed(ecl[0], ecl[1], ecl[3], ecl[4])
        else:
            return EclCoord(ecl[0], ecl[1])

    def swe_equator_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EquatorCoord | EquatorSpeed:
        if mean is not False:
            raise RuntimeError("mean position flag has no meaning for the planets")
        iflag = swe.FLG_SWIEPH | swe.FLG_TOPOCTR | swe.FLG_EQUATORIAL
        if speed:
            iflag |= swe.FLG_SPEED
        (equator, _) = swe.calc_ut(jd, self.__swe_code, iflag)
        if speed:
            return EquatorSpeed(equator[0], equator[1], equator[3], equator[4])
        else:
            return EquatorCoord(equator[0], equator[1])


class ApsisNode(Celestial):
    """Planet apsides and nodes"""

    def __init__(self, name: str, swe_code: int | NoneType = None):
        self.name = name
        self.__swe_code = swe_code or Celestial.swe_id_by_name(name)

    def _swe_ecl_coord_nod_aps(self, jd, *, speed: bool = False, mean: bool = False, equatorial: bool = False, second_focus: bool = False):
        method = swe.NODBIT_MEAN if mean else swe.NODBIT_OSCU
        if second_focus:
            method |= swe.NODBIT_FOPOINT
        iflag = swe.FLG_SWIEPH | swe.FLG_TOPOCTR
        if speed:
            iflag |= swe.FLG_SPEED
        if equatorial:
            iflag |= swe.FLG_EQUATORIAL
        return swe.nod_aps_ut(jd, self.__swe_code, method, iflag)

    def swe_id(self) -> int:
        return self.__swe_code

    def is_fixed(self) -> bool:
        return False

    def is_focal_point(self) -> bool:
        return True


class SecondFocus(ApsisNode):
    """Second focal point of some planet orbit"""

    def swe_ecl_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EclCoord:
        (_, _, _, ecl) = super()._swe_ecl_coord_nod_aps(jd, speed=speed, mean=mean, equatorial=False, second_focus=True)
        if speed:
            return EclSpeed(ecl[0], ecl[1], ecl[3], ecl[4])
        else:
            return EclCoord(ecl[0], ecl[1])

    def swe_equator_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EquatorCoord:
        (_, _, _, equator) = super()._swe_ecl_coord_nod_aps(jd, speed=speed, mean=mean, equatorial=True, second_focus=True)
        if speed:
            return EquatorSpeed(equator[0], equator[1], equator[3], equator[4])
        else:
            return EquatorCoord(equator[0], equator[1])


class ApoApsis(ApsisNode):
    """Aphelion/apogee of some planet orbit"""

    def swe_ecl_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EclCoord:
        (_, _, _, ecl) = super()._swe_ecl_coord_nod_aps(jd, speed=speed, mean=mean, equatorial=False)
        if speed:
            return EclSpeed(ecl[0], ecl[1], ecl[3], ecl[4])
        else:
            return EclCoord(ecl[0], ecl[1])

    def swe_equator_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EquatorCoord:
        (_, _, _, equator) = super()._swe_ecl_coord_nod_aps(jd, speed=speed, mean=mean, equatorial=True)
        if speed:
            return EquatorSpeed(equator[0], equator[1], equator[3], equator[4])
        else:
            return EquatorCoord(equator[0], equator[1])


class PeriApsis(ApsisNode):
    """Perihelion/perigee of some planet orbit"""

    def swe_ecl_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EclCoord:
        (_, _, ecl, _) = super()._swe_ecl_coord_nod_aps(jd, speed=speed, mean=mean, equatorial=False)
        if speed:
            return EclSpeed(ecl[0], ecl[1], ecl[3], ecl[4])
        else:
            return EclCoord(ecl[0], ecl[1])

    def swe_equator_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EquatorCoord:
        (_, _, equator, _) = super()._swe_ecl_coord_nod_aps(jd, speed=speed, mean=mean, equatorial=True)
        if speed:
            return EquatorSpeed(equator[0], equator[1], equator[3], equator[4])
        else:
            return EquatorCoord(equator[0], equator[1])


class AscNode(ApsisNode):
    """Ascending node of some planet orbit"""

    def swe_ecl_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EclCoord:
        (ecl, _, _, _) = super()._swe_ecl_coord_nod_aps(jd, speed=speed, mean=mean, equatorial=False)
        if speed:
            return EclSpeed(ecl[0], ecl[1], ecl[3], ecl[4])
        else:
            return EclCoord(ecl[0], ecl[1])

    def swe_equator_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EquatorCoord:
        (equator, _, _, _) = super()._swe_ecl_coord_nod_aps(jd, speed=speed, mean=mean, equatorial=True)
        if speed:
            return EquatorSpeed(equator[0], equator[1], equator[3], equator[4])
        else:
            return EquatorCoord(equator[0], equator[1])


class DscNode(ApsisNode):
    """Descending node of some planet orbit"""

    def swe_ecl_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EclCoord:
        (_, ecl, _, _) = super()._swe_ecl_coord_nod_aps(jd, speed=speed, mean=mean, equatorial=False)
        if speed:
            return EclSpeed(ecl[0], ecl[1], ecl[3], ecl[4])
        else:
            return EclCoord(ecl[0], ecl[1])

    def swe_equator_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EquatorCoord:
        (_, equator, _, _) = super()._swe_ecl_coord_nod_aps(jd, speed=speed, mean=mean, equatorial=True)
        if speed:
            return EquatorSpeed(equator[0], equator[1], equator[3], equator[4])
        else:
            return EquatorCoord(equator[0], equator[1])


class FixedCelestial(Celestial):
    """Fixed astronomical objects: stars, galactic and deep space objects"""

    def __init__(self, name: str, swe_code: str):
        self.name = name
        self.__swe_code = swe_code

    def swe_id(self):
        return self.__swe_code

    def is_fixed(self) -> bool:
        return True

    def is_focal_point(self) -> bool:
        return False

    def swe_ecl_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EclCoord:
        if mean is not False:
            raise RuntimeError("mean position flag has no meaning for fixed objects")
        iflag = swe.FLG_SWIEPH | swe.FLG_TOPOCTR
        if speed:
            iflag |= swe.FLG_SPEED
        (ecl, _, _) = swe.fixstar_ut(self.__swe_code, jd, iflag)
        if speed:
            return EclSpeed(ecl[0], ecl[1], ecl[3], ecl[4])
        else:
            return EclCoord(ecl[0], ecl[1])

    def swe_equator_coord(self, jd, *, speed: bool = False, mean: bool = False) -> EquatorCoord:
        if mean is not False:
            raise RuntimeError("mean position flag has no meaning for fixed objects")
        iflag = swe.FLG_SWIEPH | swe.FLG_TOPOCTR | swe.FLG_EQUATORIAL
        if speed:
            iflag |= swe.FLG_SPEED
        (equator, _, _) = swe.fixstar_ut(self.__swe_code, jd, iflag)
        if speed:
            return EquatorSpeed(equator[0], equator[1], equator[3], equator[4])
        else:
            return EquatorCoord(equator[0], equator[1])


Planet.Sun = Planet("Sun")
Planet.Moon = Planet("Moon")
Planet.Mercury = Planet("Mercury")
Planet.Venus = Planet("Venus")
Planet.Earth = Planet("Earth")
Planet.Mars = Planet("Mars")
Planet.Jupiter = Planet("Jupiter")
Planet.Saturn = Planet("Saturn")
Planet.Uranus = Planet("Uranus")
Planet.Neptune = Planet("Neptune")
Planet.Pluto = Planet("Pluto")

Planet.septener = [Planet.Sun, Planet.Mars, Planet.Moon, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn]
Planet.novile = Planet.septener + [Planet.Uranus, Planet.Neptune]

SecondFocus.Moon = SecondFocus("BE Moon", swe.MOON)
SecondFocus.Mercury = SecondFocus("BS Mercury", swe.MERCURY)
SecondFocus.Venus = SecondFocus("BS Venus", swe.VENUS)
SecondFocus.Earth = SecondFocus("BS Earth", swe.EARTH)
SecondFocus.Mars = SecondFocus("BS Mars", swe.MARS)
SecondFocus.Jupiter = SecondFocus("BS Jupiter", swe.JUPITER)
SecondFocus.Saturn = SecondFocus("BS Saturn", swe.SATURN)
SecondFocus.Uranus = SecondFocus("BS Uranus", swe.URANUS)
SecondFocus.Neptune = SecondFocus("BS Neptune", swe.NEPTUNE)
