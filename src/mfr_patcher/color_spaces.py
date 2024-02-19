import math
from enum import Enum
from typing import Any


class RgbBitSize(Enum):
    Rgb5 = 1
    Rgb8 = 2


class RgbColor:
    """Color represented as RGB using 5 or 8 bits per channel."""

    FACTOR = 255.0

    def __init__(self, R: int, G: int, B: int, bit_size: RgbBitSize):
        if bit_size == RgbBitSize.Rgb5:
            R <<= 3
            G <<= 3
            B <<= 3
        elif bit_size == RgbBitSize.Rgb8:
            self.red = R
            self.green = G
            self.blue = B
        elif bit_size != RgbBitSize.Rgb8:
            raise ValueError(bit_size)
        self.red = R
        self.green = G
        self.blue = B

    @classmethod
    def from_rgb(cls, rgb: int, bit_size: RgbBitSize) -> "RgbColor":
        if bit_size == RgbBitSize.Rgb5:
            r = (rgb & 0x1F) << 3
            g = (rgb & 0x3E0) >> 2
            b = (rgb & 0x7C00) >> 7
        elif bit_size == RgbBitSize.Rgb8:
            r = (rgb >> 16) & 0xFF
            g = (rgb >> 8) & 0xFF
            b = rgb & 0xFF
        else:
            raise ValueError(bit_size)
        return RgbColor(r, g, b, RgbBitSize.Rgb8)

    def __str__(self) -> str:
        return self.hex_15()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, RgbColor):
            return self.rgb_24() == other.rgb_24()
        return False

    def __hash__(self) -> int:
        return self.rgb_24()

    def hsv(self) -> "HsvColor":
        r = self.r_fraction()
        g = self.g_fraction()
        b = self.b_fraction()
        channels = [r, g, b]
        channels.sort()

        # get value
        c_min = channels[0]
        c_max = channels[2]
        v = c_max

        # get hue
        c_range = c_max - c_min
        if c_range == 0:
            h = 0.0
        else:
            if c_max == r:
                h = 60 * ((g - b) / c_range)
            elif c_max == g:
                h = 60 * ((b - r) / c_range + 2)
            elif c_max == b:
                h = 60 * ((r - g) / c_range + 4)
            # check if negative
            if h < 0:
                h += 360

        # get saturation
        if v == 0:
            s = 0
        else:
            s = c_range / v

        return HsvColor(h, s, v)

    def lab(self) -> "LabColor":
        # convert to linear rgb
        r = self.scale_rgb(self.r_fraction())
        g = self.scale_rgb(self.g_fraction())
        b = self.scale_rgb(self.b_fraction())

        # convert to xyz
        x = r * 0.4124 + g * 0.3576 + b * 0.1805
        y = r * 0.2126 + g * 0.7152 + b * 0.0722
        z = r * 0.0193 + g * 0.1192 + b * 0.9505

        # reference illuminant
        x /= 0.950489
        # y /= 1
        z /= 1.088840

        # scale xyz
        x = self.scale_xyz(x)
        y = self.scale_xyz(y)
        z = self.scale_xyz(z)

        return LabColor(116 * y - 16, 500 * (x - y), 200 * (y - z))

    def luma(self) -> float:
        return 0.299 * self.red + 0.587 * self.green + 0.114 * self.blue

    def r_5(self) -> int:
        return self.red >> 3

    def g_5(self) -> int:
        return self.green >> 3

    def b_5(self) -> int:
        return self.blue >> 3

    def rgb_15(self) -> int:
        return (self.b_5() << 10) | (self.g_5() << 5) | self.r_5()

    def rgb_24(self) -> int:
        return (self.blue << 16) | (self.green << 8) | self.red

    def hex_15(self) -> str:
        return f"{self.rgb_15():04X}"

    def r_fraction(self) -> float:
        return self.red / self.FACTOR

    def g_fraction(self) -> float:
        return self.green / self.FACTOR

    def b_fraction(self) -> float:
        return self.blue / self.FACTOR

    @classmethod
    def black(cls) -> "RgbColor":
        return RgbColor.from_rgb(0, RgbBitSize.Rgb8)

    @classmethod
    def white_5(cls) -> "RgbColor":
        return RgbColor.from_rgb(0x7FFF, RgbBitSize.Rgb5)

    @staticmethod
    def scale_rgb(value: float) -> float:
        if value > 0.04045:
            return math.pow((value + 0.055) / 1.055, 2.4)
        return value / 12.92

    @staticmethod
    def scale_xyz(value: float) -> float:
        if value > 0.008856:
            return math.pow(value, 0.333333)
        return 7.78704 * value + 0.137931


class HsvColor:
    """
    Color represented as HSV, where 0 <= hue <= 360,
    0 <= saturation <= 1, and 0 <= value <= 1.
    """

    def __init__(self, hue: float, saturation: float, value: float):
        self.hue = hue
        self.saturation = saturation
        self.value = value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, HsvColor):
            return (
                self.hue == other.hue
                and self.saturation == other.saturation
                and self.value == other.value
            )
        return False

    def __hash__(self) -> int:
        return hash(self.hue) ^ hash(self.saturation) ^ hash(self.value)

    def rgb(self) -> RgbColor:
        c = self.value * self.saturation
        hp = self.hue / 60
        x = c * (1 - abs(hp % 2 - 1))

        if hp < 1:
            rgb = (c, x, 0)
        elif hp < 2:
            rgb = (x, c, 0)
        elif hp < 3:
            rgb = (0, c, x)
        elif hp < 4:
            rgb = (0, x, c)
        elif hp < 5:
            rgb = (x, 0, c)
        else:
            rgb = (c, 0, x)

        m = self.value - c
        factor = RgbColor.FACTOR
        r = round((rgb[0] + m) * factor)
        g = round((rgb[1] + m) * factor)
        b = round((rgb[2] + m) * factor)
        return RgbColor(r, g, b, RgbBitSize.Rgb8)


class LabColor:
    """
    Color represented as LAB, where 0 <= L <= 100,
    A and B are typically between -100 and 100.
    """

    def __init__(self, L: float, A: float, B: float):
        self.l_star = L
        self.a_star = A
        self.b_star = B

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, LabColor):
            return (
                self.l_star == other.l_star
                and self.a_star == other.a_star
                and self.b_star == other.b_star
            )
        return False

    def __hash__(self) -> int:
        return hash(self.l_star) ^ hash(self.a_star) ^ hash(self.b_star)

    def rgb(self) -> RgbColor:
        # convert to XYZ
        y = (self.l_star + 16) / 116
        x = self.a_star / 500 + y
        z = y - self.b_star / 200

        # scale XYZ
        x = self.scale_xyz(x)
        y = self.scale_xyz(y)
        z = self.scale_xyz(z)

        # reference illuminant
        x *= 0.950489
        # y *= 1
        z *= 1.088840

        # convert to RGB linear
        rf = x * 3.2406 + y * -1.5372 + z * -0.4986
        gf = x * -0.9689 + y * 1.8758 + z * 0.0415
        bf = x * 0.0557 + y * -0.2040 + z * 1.0570

        # gamma coorection
        rf = self.scale_rgb(rf)
        gf = self.scale_rgb(gf)
        bf = self.scale_rgb(bf)

        r = int(round(rf * 255))
        g = int(round(gf * 255))
        b = int(round(bf * 255))

        return RgbColor(
            max(0, min(r, 255)), max(0, min(g, 255)), max(0, min(b, 255)), RgbBitSize.Rgb8
        )

    def hue(self) -> float:
        """Gets the hue measured in radians. Ranges from -pi to pi."""
        return math.atan2(self.b_star, self.a_star)

    def chroma(self) -> float:
        """
        The intensity or purity of a color, i.e. how far it is from a
        neutral gray of the same lightness."""
        return math.sqrt(self.a_star * self.a_star + self.b_star * self.b_star)

    def shift_hue(self, shift: float) -> "LabColor":
        """Shifts hue by the provided amount, measured in radians."""
        # get hue in range 0 to 2pi
        hue = self.hue() + math.pi
        hue = (hue + shift) % (2 * math.pi)
        # put hue back in range -pi to pi
        hue -= math.pi

        # get new A and B values
        chroma = self.chroma()
        a = chroma * math.cos(hue)
        b = chroma * math.sin(hue)
        return LabColor(self.l_star, a, b)

    @staticmethod
    def scale_xyz(value: float) -> float:
        if value > 0.206897:
            return math.pow(value, 3)
        return (value - 0.137931) / 7.78704

    @staticmethod
    def scale_rgb(value: float) -> float:
        if value > 0.0031308:
            return 1.055 * math.pow(value, 1 / 2.4) - 0.055
        return value * 12.92
