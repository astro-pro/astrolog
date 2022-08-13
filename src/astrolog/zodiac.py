from .primitives import Angle


class Zodiac:
    def __init__(self, name: str, symbol: chr, offset: int):
        self.name = name
        self.abbr = name[:3]
        self.symbol = symbol
        self.offset = offset

    @classmethod
    def from_longitude(cls, longitude: Angle):
        for sign in Zodiac.all:
            if sign.offset <= longitude.degrees < sign.offset + 30:
                return sign


class ZodiacConstell:
    def __init__(self, name: str, symbol: chr, from_lng: float, upto_lng: float):
        self.name = name
        self.abbr = name[:3]
        self.symbol = symbol
        self.from_lng = from_lng
        self.upto_lng = upto_lng

    @classmethod
    def from_longitude(cls, longitude: Angle):
        for sign in ZodiacConstell.all:
            if sign.from_lng > sign.upto_lng and (
                0 <= longitude.degrees < sign.upto_lng or
                sign.upto_lng <= longitude.degrees <= 360
            ):
                return sign
            elif sign.from_lng <= longitude.degrees < sign.upto_lng:
                return sign


Zodiac.Aries = Zodiac("Aries", '♈', 0)
Zodiac.Taurus = Zodiac("Taurus", '♉', 30)
Zodiac.Gemini = Zodiac("Gemini", '♊', 60)
Zodiac.Cancer = Zodiac("Cancer", '♋', 90)
Zodiac.Leo = Zodiac("Leo", '♌', 120)
Zodiac.Virgo = Zodiac("Virgo", '♍', 150)
Zodiac.Libra = Zodiac("Libra", '♎', 180)
Zodiac.Scorpio = Zodiac("Scorpio", '♏', 210)
Zodiac.Sagittarius = Zodiac("Sagittarius", '♐', 240)
Zodiac.Capricorn = Zodiac("Capricorn", '♑', 270)
Zodiac.Aquarius = Zodiac("Aquarius", '♒', 300)
Zodiac.Pisces = Zodiac("Pisces", '♓', 330)

Zodiac.all = [Zodiac.Aries, Zodiac.Taurus, Zodiac.Gemini, Zodiac.Cancer, Zodiac.Leo, Zodiac.Virgo,
              Zodiac.Libra, Zodiac.Scorpio, Zodiac.Sagittarius, Zodiac.Capricorn, Zodiac.Aquarius, Zodiac.Pisces]

ZodiacConstell.Aries = ZodiacConstell("Aries", '♈', 29.09, 53.47)
ZodiacConstell.Taurus = ZodiacConstell("Taurus", '♉', 53.47, 90.43)
ZodiacConstell.Gemini = ZodiacConstell("Gemini", '♊', 90.43, 118.26)
ZodiacConstell.Cancer = ZodiacConstell("Cancer", '♋', 118.26, 138.18)
ZodiacConstell.Leo = ZodiacConstell("Leo", '♌', 138.18, 174.16)
ZodiacConstell.Virgo = ZodiacConstell("Virgo", '♍', 174.16, 217.80)
ZodiacConstell.Libra = ZodiacConstell("Libra", '♎', 217.80, 241.14)
ZodiacConstell.Scorpio = ZodiacConstell("Scorpio", '♏', 241.14, 248.04)
ZodiacConstell.Ophiuchus = ZodiacConstell("Ophiuchus", '⛎', 248.04, 266.61)
ZodiacConstell.Sagittarius = ZodiacConstell("Sagittarius", '♐', 266.61, 299.71)
ZodiacConstell.Capricorn = ZodiacConstell("Capricorn", '♑', 299.71, 327.89)
ZodiacConstell.Aquarius = ZodiacConstell("Aquarius", '♒', 327.89, 351.57)
ZodiacConstell.Pisces = ZodiacConstell("Pisces", '♓', 351.57, 29.09)

ZodiacConstell.all = [ZodiacConstell.Aries, ZodiacConstell.Taurus, ZodiacConstell.Gemini, ZodiacConstell.Cancer,
                      ZodiacConstell.Leo, ZodiacConstell.Virgo, ZodiacConstell.Libra, ZodiacConstell.Scorpio,
                      ZodiacConstell.Ophiuchus, ZodiacConstell.Sagittarius, ZodiacConstell.Capricorn,
                      ZodiacConstell.Aquarius, ZodiacConstell.Pisces]
