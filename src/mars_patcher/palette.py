import math

from mars_patcher.color_spaces import RgbBitSize, RgbColor
from mars_patcher.rom import Rom


class Palette:
    def __init__(self, rows: int, rom: Rom, addr: int):
        assert rows >= 1
        self.colors: list[RgbColor] = []
        for i in range(rows * 16):
            rgb = rom.read_16(addr + i * 2)
            color = RgbColor.from_rgb(rgb, RgbBitSize.Rgb5)
            self.colors.append(color)

    def __getitem__(self, key: int) -> RgbColor:
        return self.colors[key]

    def rows(self) -> int:
        return len(self.colors) // 16

    def byte_data(self) -> bytes:
        arr = bytearray()
        for color in self.colors:
            val = color.rgb_15()
            arr.append(val & 0xFF)
            arr.append(val >> 8)
        return bytes(arr)

    def write(self, rom: Rom, addr: int) -> None:
        data = self.byte_data()
        rom.write_bytes(addr, data)

    def shift_hue_hsv(self, shift: int, excluded_rows: set[int]) -> None:
        """
        Shifts hue by the provided amount, measured in degrees.
        Uses HSV color space.
        """
        black = RgbColor.black()
        white = RgbColor.white_5()
        for row in range(self.rows()):
            if row in excluded_rows:
                continue
            offset = row * 16
            for i in range(16):
                # Skip black and white
                rgb = self.colors[offset + i]
                if rgb == black or rgb == white:
                    continue
                # Get HSV and shift hue
                orig_luma = rgb.luma()
                hsv = rgb.hsv()
                hsv.hue = (hsv.hue + shift) % 360
                # Get new RGB and rescale luma
                rgb = hsv.rgb()
                luma_ratio = orig_luma / rgb.luma()
                rgb.red = min(int(rgb.red * luma_ratio), 255)
                rgb.green = min(int(rgb.green * luma_ratio), 255)
                rgb.blue = min(int(rgb.blue * luma_ratio), 255)
                self.colors[offset + i] = rgb

    def shift_hue_oklab(self, shift: int, excluded_rows: set[int]) -> None:
        """
        Shifts hue by the provided amount, measured in degrees.
        Uses Oklab color space.
        """
        # Convert shift to radians
        shift_rads = shift * (math.pi / 180)
        for row in range(self.rows()):
            if row in excluded_rows:
                continue
            offset = row * 16
            for i in range(16):
                rgb = self.colors[offset + i]
                lab = rgb.oklab().shift_hue(shift_rads)
                self.colors[offset + i] = lab.rgb()
