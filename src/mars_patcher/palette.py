import math
import random
from enum import Enum

from mars_patcher.color_spaces import HsvColor, OklabColor, RgbBitSize, RgbColor
from mars_patcher.rom import Rom


class VariationType(Enum):
    ADD = 0
    MULTIPLY = 1


class PaletteVariation:
    def __init__(self, start: float, step: float):
        self.start = start
        self.step = step

    def get_at(self, index: int) -> float:
        assert 0 <= index < 16
        return self.start + (index * self.step)

    @staticmethod
    def generate(max_range: float, type: VariationType) -> "PaletteVariation":
        """
        Generates a list of 16 floats that vary within a specified range, with
        values that either increase or decrease.

        Add example 1: [-40, -35, ..., -5, 0, ..., 30, 35]
        Add example 2: [0.08, 0.06, ..., -0.06, -0.08, ..., -0.20, -0.22]
        Multiply example 1: [0.60, 0.65, ..., 0.95, 1.00, ..., 1.30, 1.35]
        Multipy example 2: [1.08, 1.06, ..., 0.94, 0.92, ..., 0.80, 0.78]
        """
        assert max_range >= 0.0
        # Generate random value between 0 and max_range
        var_range = random.uniform(max_range / 4, max_range)
        # var_range = max_range
        if type == VariationType.ADD:
            start = random.uniform(-var_range, 0)
        elif type == VariationType.MULTIPLY:
            start = random.uniform(1.0 - var_range, 1.0)
        else:
            raise ValueError("Invalid VariationType")
        step = var_range / 16.0
        # Choose randomly between increasing or decreasing values
        if random.choice([True, False]):
            start += 15 * step
            step = -step
        return PaletteVariation(start, step)


class ColorChange:
    def __init__(
        self,
        hue_shift: float,
        hue_var: PaletteVariation | None,
        lightness_var: PaletteVariation | None,
    ):
        self.hue_shift = hue_shift
        self.hue_var = hue_var
        self.lightness_var = lightness_var

    def change_hsv(self, hsv: HsvColor, index: int) -> HsvColor:
        shift = self.hue_shift
        if self.hue_var is not None:
            shift += self.hue_var.get_at(index)
        hsv.hue = (hsv.hue + shift) % 360
        if self.lightness_var is not None:
            hsv.value = min(hsv.value * self.lightness_var.get_at(index), 1.0)
        return hsv

    def change_oklab(self, lab: OklabColor, index: int) -> OklabColor:
        shift = self.hue_shift
        if self.hue_var is not None:
            shift += self.hue_var.get_at(index)
        # Convert hue shift to radians
        shift *= math.pi / 180
        lab = lab.shift_hue(shift)
        if self.lightness_var is not None:
            lab.l_star = min(lab.l_star * self.lightness_var.get_at(index), 1.0)
        return lab


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

    def change_colors_hsv(self, change: ColorChange, excluded_rows: set[int]) -> None:
        """Apply a color change using HSV color space."""
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
                orig_luma = rgb.luma()
                hsv = change.change_hsv(rgb.hsv(), i)
                rgb = hsv.rgb()
                # Rescale luma
                luma_ratio = orig_luma / rgb.luma()
                rgb.red = min(int(rgb.red * luma_ratio), 255)
                rgb.green = min(int(rgb.green * luma_ratio), 255)
                rgb.blue = min(int(rgb.blue * luma_ratio), 255)
                self.colors[offset + i] = rgb

    def change_colors_oklab(self, change: ColorChange, excluded_rows: set[int]) -> None:
        """Apply a color change using Oklab color space."""
        # Convert shift to radians
        for row in range(self.rows()):
            if row in excluded_rows:
                continue
            offset = row * 16
            for i in range(16):
                rgb = self.colors[offset + i]
                lab = change.change_oklab(rgb.oklab(), i)
                self.colors[offset + i] = lab.rgb()
