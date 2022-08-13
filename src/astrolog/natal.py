from datetime import datetime, time, timedelta
import swisseph as swe

from .celestials import Celestial
from .primitives import GeoLocation
from .coords import HorCoord, EclCoord
from .zodiac import Zodiac, ZodiacConstell


class NatalObject:
    """Natal object computable type"""

    def __init__(self, obj: Celestial, birth: datetime, place: GeoLocation):
        self.name = obj.name
        self.obj = obj
        self.birth = birth
        self.place = place
        self.__ecl_coord = None
        self.__transits = None

    def julday(self) -> float:
        return swe.julday(self.birth.year, self.birth.month, self.birth.day, self.birth.hour + self.birth.minute / 60.)

    def ecl_coord(self) -> EclCoord:
        if self.__ecl_coord is None:
            self.__ecl_coord = self.obj.swe_ecl_coord(self.julday())
        return self.__ecl_coord

    def hor_coord(self) -> HorCoord:
        coord = self.ecl_coord()
        geopos = (self.place.longitude.degrees, self.place.latitude.degrees, 0.0)
        pos = (coord.longitude.degrees, coord.latitude.degrees, 0.0)
        atpress = 0
        attemp = 0
        (azimuth, true_alt, app_alt) = swe.azalt(self.julday(), swe.ECL2HOR, geopos, atpress, attemp, pos)
        return HorCoord(azimuth, true_alt)

    def sign_pos(self) -> (Zodiac, float):
        return self.ecl_coord().sign_pos()

    def constell_pos(self) -> (ZodiacConstell, float):
        return self.ecl_coord().constell_pos()

    def house_pos(self) -> (int, float):
        return self.hor_coord().house_pos()

    def transits(self) -> dict:
        if self.__transits is None:
            self.__transits = self.obj.transits(self.birth, self.place)
        return self.__transits


class Natal:
    """Natal chart"""

    def __init__(self, person: str, birth: datetime, place: GeoLocation, celestials: [Celestial]):
        self.person = person
        self.birth = birth
        self.place = place
        self.celestials = {obj: NatalObject(obj, birth, place) for obj in celestials}
        swe.set_topo(self.place.longitude.degrees, self.place.latitude.degrees)

    def __iter__(self):
        for cel in self.celestials:
            yield self.celestials[cel]

    def __getitem__(self, celestial: Celestial) -> NatalObject:
        return self.celestials[celestial]

    def aspects(self, orb: float = 1.01, of=None, to=None):
        if type(of) is list:
            list1 = of
        elif isinstance(of, Celestial):
            list1 = [of]
        else:
            list1 = self.celestials

        if type(to) is list:
            list2 = to
        elif isinstance(to, Celestial):
            list2 = [to]
        else:
            list2 = self.celestials

        for (i1, cel1) in enumerate(list1):
            for (i2, cel2) in enumerate(list2):
                if cel1 == cel2:
                    break
                angle = self[cel1].ecl_coord() ^ self[cel2].ecl_coord()
                aspect = angle.aspect(orb=orb)
                if aspect is None:
                    continue
                yield {"first": cel1.name, "second": cel2.name, "aspect": aspect}

    def parans(self, orb: timedelta = timedelta(minutes=5)) -> list:
        events = []
        timeline = {}
        for cel in self:
            transits = cel.transits()
            for transit_name in transits:
                transit_time = transits[transit_name]
                if transit_time is None:
                    continue
                for tm in timeline:
                    if abs(tm - transit_time) <= orb:
                        events.append([
                            timeline[tm],
                            (transit_name, cel.obj)
                        ])
                timeline[transit_time] = (transit_name, cel.obj)
        return events
