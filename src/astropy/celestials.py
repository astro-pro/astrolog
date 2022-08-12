from abc import ABC, abstractmethod
from datetime import datetime, time, timedelta
import swisseph as swe

from . import GeoLocation, EclCoord, EquatorCoord, HorCoord


class Celestial(ABC):
    """Abstract class for celestial objects whose location can be computed"""

    def ecl_coord(self, time: datetime, location: GeoLocation) -> EclCoord:
        swe.set_topo(location.longitude.degrees, location.latitude.degrees)
        jd = swe.julday(time.year, time.month, time.day, time.hour + time.minute / 60.)
        return self.swe_ecl_coord(jd)

    def equator_coord(self, time: datetime, location: GeoLocation) -> EquatorCoord:
        swe.set_topo(location.longitude.degrees, location.latitude.degrees)
        jd = swe.julday(time.year, time.month, time.day, time.hour + time.minute / 60.)
        return self.swe_equator_coord(jd)

    def hor_coord(self, time: datetime, location: GeoLocation) -> HorCoord:
        swe.set_topo(location.longitude.degrees, location.latitude.degrees)
        jd = swe.julday(time.year, time.month, time.day, time.hour + time.minute / 60.)
        coord = self.swe_equator_coord(jd)
        geopos = (location.longitude.degrees, location.latitude.degrees, 0.0)
        pos = (coord.ra.degrees, coord.decl.degrees, 0.0)
        atpress = 0
        attemp = 0
        (azimuth, true_alt, app_alt) = swe.azalt(jd, swe.EQU2HOR, geopos, atpress, attemp, pos)
        return HorCoord(azimuth, true_alt)

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

    @abstractmethod
    def is_fixed(self) -> bool:
        pass

    @abstractmethod
    def is_focal_point(self) -> bool:
        pass

    @abstractmethod
    def swe_ecl_coord(self, jd) -> EclCoord:
        pass

    @abstractmethod
    def swe_equator_coord(self, jd) -> EquatorCoord:
        pass


class Planet(Celestial):
    """Planets (moving physical bodies)"""

    def __init__(self, name: str, swe_code: int):
        self.name = name
        self.__swe_code = swe_code

    def swe_id(self):
        return self.__swe_code

    def is_fixed(self) -> bool:
        return False

    def is_focal_point(self) -> bool:
        return False

    def swe_ecl_coord(self, jd) -> EclCoord:
        (ecl, _) = swe.calc_ut(jd, self.__swe_code, swe.FLG_SWIEPH | swe.FLG_TOPOCTR)
        return EclCoord(ecl[0], ecl[1])

    def swe_equator_coord(self, jd) -> EquatorCoord:
        (equator, _) = swe.calc_ut(jd, self.__swe_code, swe.FLG_SWIEPH | swe.FLG_TOPOCTR | swe.FLG_EQUATORIAL)
        return EquatorCoord(equator[0], equator[1])


class BlackSun(Celestial):
    """Second focal point of some planet orbit"""

    def __init__(self, name: str, swe_code: int):
        self.name = name
        self.__swe_code = swe_code

    def swe_id(self) -> int:
        return self.__swe_code

    def is_fixed(self) -> bool:
        return False

    def is_focal_point(self) -> bool:
        return True

    def swe_ecl_coord(self, jd) -> EclCoord:
        (_, _, _, ecl) = swe.nod_aps_ut(jd, self.__swe_code,
                                        swe.NODBIT_FOPOINT | swe.NODBIT_OSCU,
                                        swe.FLG_SWIEPH | swe.FLG_TOPOCTR)
        return EclCoord(ecl[0], ecl[1])

    def swe_equator_coord(self, jd) -> EquatorCoord:
        (_, _, _, equator) = swe.nod_aps_ut(jd, self.__swe_code,
                                        swe.NODBIT_FOPOINT | swe.NODBIT_OSCU,
                                        swe.FLG_SWIEPH | swe.FLG_TOPOCTR | swe.FLG_EQUATORIAL)
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

    def swe_ecl_coord(self, jd) -> EclCoord:
        (ecl, _, _) = swe.fixstar_ut(self.__swe_code, jd, swe.FLG_SWIEPH | swe.FLG_TOPOCTR)
        return EclCoord(ecl[0], ecl[1])

    def swe_equator_coord(self, jd) -> EquatorCoord:
        (equator, _, _) = swe.fixstar_ut(self.__swe_code, jd, swe.FLG_SWIEPH | swe.FLG_TOPOCTR | swe.FLG_EQUATORIAL)
        return EquatorCoord(equator[0], equator[1])


Planet.Sun = Planet("Sun", swe.SUN)
Planet.Moon = Planet("Moon", swe.MOON)
Planet.Mercury = Planet("Mercury", swe.MERCURY)
Planet.Venus = Planet("Venus", swe.VENUS)
Planet.Earth = Planet("Earth", swe.EARTH)
Planet.Mars = Planet("Mars", swe.MARS)
Planet.Jupiter = Planet("Jupiter", swe.JUPITER)
Planet.Saturn = Planet("Saturn", swe.SATURN)
Planet.Uranus = Planet("Uranus", swe.URANUS)
Planet.Neptune = Planet("Neptune", swe.NEPTUNE)
Planet.Pluto = Planet("Pluto", swe.PLUTO)

Planet.septener = [Planet.Sun, Planet.Mars, Planet.Moon, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn]
Planet.novile = Planet.septener + [Planet.Uranus, Planet.Neptune]

BlackSun.BlackEarth = BlackSun("Black Earth", swe.MOON)
BlackSun.Mercury = BlackSun("BS Mercury", swe.MERCURY)
BlackSun.Venus = BlackSun("BS Venus", swe.VENUS)
BlackSun.Earth = BlackSun("BS Earth", swe.EARTH)
BlackSun.Mars = BlackSun("BS Mars", swe.MARS)
BlackSun.Jupiter = BlackSun("BS Jupiter", swe.JUPITER)
BlackSun.Saturn = BlackSun("BS Saturn", swe.SATURN)
BlackSun.Uranus = BlackSun("BS Uranus", swe.URANUS)
BlackSun.Neptune = BlackSun("BS Neptune", swe.NEPTUNE)
