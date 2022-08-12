from dms2dec.dms_convert import dms2dec
import math


class Angle:
    """Angle measured in degrees"""

    def __init__(self, *arg, **kwarg):
        if len(arg) > 0:
            deg = arg[0]
            if type(deg) is str:
                self.degrees = dms2dec(deg)
            elif type(deg) is float or type(deg) is int:
                self.degrees = deg
        elif 'radians' in kwarg:
            self.degrees = kwarg['radians'] * 180 / math.pi

    def radians(self):
        return self.degrees * 2 * math.pi / 360

    def aspect(self, orb: float = 0.5):
        if -orb <= self.degrees <= orb:
            return 1
        for div in range(2, 14):
            angle = 360 / div
            if angle - orb <= self.degrees <= angle + orb:
                return div
        return None


class GeoLocation:
    """Location on the earth"""

    def __init__(self, longitude, latitude):
        self.longitude = Angle(longitude)
        self.latitude = Angle(latitude)
