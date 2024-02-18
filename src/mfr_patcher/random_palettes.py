from enum import Enum
import json
import random
from typing import Any, Dict, List, Tuple

from mfr_patcher.palette import Palette
from mfr_patcher.rom import Rom
from mfr_patcher.data import get_data_path


class PaletteType(Enum):
    TILESETS = 1
    ENEMIES = 2
    SAMUS = 3
    BEAMS = 4


class ColorSpace(Enum):
    HSV = 1
    LAB = 2


class PaletteSettings(object):
    TYPE_ENUMS = {
        "Tilesets": PaletteType.TILESETS,
        "Enemies": PaletteType.ENEMIES,
        "Samus": PaletteType.SAMUS,
        "Beams": PaletteType.BEAMS
    }

    def __init__(self,
        seed: int,
        pal_types: List[PaletteType],
        hue_min: int,
        hue_max: int,
        color_space: ColorSpace
    ):
        self.seed = seed
        self.pal_types = pal_types
        self.hue_min = hue_min
        self.hue_max = hue_max
        self.color_space = color_space

    @classmethod
    def from_json(cls, data: Any) -> "PaletteSettings":
        seed = data.get("Seed", random.randint(0, 2**31 - 1))
        random.seed(seed)
        pal_types = [cls.TYPE_ENUMS[t] for t in data["Randomize"]]
        hue_min = data.get("HueMin")
        hue_max = data.get("HueMax")
        if hue_min is None or hue_max is None:
            if hue_max is not None:
                hue_min = random.randint(0, hue_max)
            elif hue_min is not None:
                hue_max = random.randint(hue_min, 180)
            else:
                hue_min = random.randint(0, 180)
                hue_max = random.randint(hue_min, 180)
        if hue_min > hue_max:
            raise ValueError("HueMin cannot be greater than HueMax")
        if "ColorSpace" in data:
            color_space = ColorSpace[data["ColorSpace"]]
        else:
            color_space = ColorSpace.LAB
        return cls(seed, pal_types, hue_min, hue_max, color_space)


class PaletteRandomizer(object):
    """Class for randomly shifting the hues of color palettes."""

    def __init__(self, rom: Rom, settings: PaletteSettings):
        self.rom = rom
        self.settings = settings
        if settings.color_space == ColorSpace.HSV:
            self.shift_func = self.shift_palette_hsv
        elif settings.color_space == ColorSpace.LAB:
            self.shift_func = self.shift_palette_lab

    @staticmethod
    def shift_palette_hsv(pal: Palette, shift: int) -> None:
        pal.shift_hue_hsv(shift)
    
    @staticmethod
    def shift_palette_lab(pal: Palette, shift: int) -> None:
        pal.shift_hue_lab(shift)

    def randomize(self) -> None:
        random.seed(self.settings.seed)
        if PaletteType.TILESETS in self.settings.pal_types:
            self.randomize_tilesets()
        if PaletteType.ENEMIES in self.settings.pal_types:
            self.randomize_enemies()
        if PaletteType.SAMUS in self.settings.pal_types:
            self.randomize_samus()
        if PaletteType.BEAMS in self.settings.pal_types:
            self.randomize_beams()
        # fix any sprite/tileset palettes that should be the same
        # TODO: check for palette fixes needed in fusion
        if self.rom.is_zm():
            self.fix_zm_palettes()        

    def get_hue_shift(self) -> int:
        """Returns a hue shift in a random direction between hue_min and hue_max."""
        shift = random.randint(self.settings.hue_min, self.settings.hue_max)
        if random.random() < 0.5:
            shift = 360 - shift
        return shift

    def shift_palettes(self, pals: List[Tuple[int, int]], shift: int) -> None:
        for addr, rows in pals:
            pal = Palette(rows, self.rom, addr)
            self.shift_func(pal, shift)
            pal.write(self.rom, addr)

    def randomize_samus(self) -> None:
        shift = self.get_hue_shift()
        self.shift_palettes(self.rom.samus_palettes(), shift)
        self.shift_palettes(self.rom.file_select_helmet_palettes(), shift)
    
    def randomize_beams(self) -> None:
        shift = self.get_hue_shift()
        self.shift_palettes(self.rom.beam_palettes(), shift)

    def randomize_tilesets(self) -> None:
        rom = self.rom
        ts_addr = rom.tileset_addr()
        ts_count = rom.tileset_count()
        randomized_pals = set()

        for _ in range(ts_count):
            pal_ptr = ts_addr + 4
            pal_addr = rom.read_ptr(pal_ptr)
            ts_addr += 0x14
            if pal_addr in randomized_pals:
                continue
            randomized_pals.add(pal_addr)
            pal = Palette(13, rom, pal_addr)
            shift = self.get_hue_shift()
            self.shift_func(pal, shift)
            pal.write(rom, pal_addr)
        
        # animated palettes
        anim_pal_addr = rom.anim_palette_addr()
        anim_pal_count = rom.anim_palette_count()
        for _ in range(anim_pal_count):
            rows = rom.read_8(anim_pal_addr + 2)
            pal_addr = rom.read_ptr(anim_pal_addr + 4)
            anim_pal_addr += 8
            if pal_addr in randomized_pals:
                continue
            randomized_pals.add(pal_addr)
            pal = Palette(rows, rom, pal_addr)
            shift = self.get_hue_shift()
            self.shift_func(pal, shift)
            pal.write(rom, pal_addr)

    def randomize_enemies(self) -> None:
        rom = self.rom
        vram_size_addr = None
        gfx_ptr = None
        if rom.is_mf():
            excluded = set()
            vram_size_addr = rom.sprite_vram_size_addr()
        elif rom.is_zm():
            excluded = {0x10, 0x11, 0x8A}
            gfx_ptr = rom.sprite_graphics_addr()
        pal_ptr = rom.sprite_palette_addr()
        sprite_count = rom.sprite_count()
        to_randomize = set(range(0x10, sprite_count))
        to_randomize -= excluded

        # go through sprites in groups
        groups = self.get_enemy_groups()
        for _, sprite_ids in groups.items():
            shift = self.get_hue_shift()
            for sprite_id in sprite_ids:
                self.randomize_enemy(sprite_id, shift, pal_ptr, vram_size_addr, gfx_ptr)
                to_randomize.remove(sprite_id)

        # go through remaining sprites
        for sprite_id in to_randomize:
            self.randomize_enemy(sprite_id, shift, pal_ptr, vram_size_addr, gfx_ptr)

    def randomize_enemy(self,
        sprite_id: int,
        shift: int,
        pal_ptr: int,
        vram_size_addr: int,
        gfx_ptr: int
    ) -> None:
        rom = self.rom
        sprite_gfx_id = sprite_id - 0x10
        pal_addr = rom.read_ptr(pal_ptr + sprite_gfx_id * 4)
        if rom.is_mf():
            vram_size = rom.read_32(vram_size_addr + sprite_gfx_id * 4)
            rows = vram_size // 0x800
        elif rom.is_zm():
            gfx_addr = rom.read_ptr(gfx_ptr + sprite_gfx_id * 4)
            rows = (rom.read_32(gfx_addr) >> 8) // 0x800
        pal = Palette(rows, rom, pal_addr)
        self.shift_func(pal, shift)
        pal.write(rom, pal_addr)

    def get_enemy_groups(self) -> Dict[str, List[int]]:
        with open(get_data_path("enemy_groups.json")) as f:
            data = json.load(f)
        return data[self.rom.game.name]

    def get_sprite_addr(self, sprite_id: int) -> int:
        addr = self.rom.sprite_palette_addr() + (sprite_id - 0x10) * 4
        return self.rom.read_ptr(addr)
    
    def get_tileset_addr(self, sprite_id: int) -> int:
        addr = self.rom.tileset_addr() + sprite_id * 0x14 + 4
        return self.rom.read_ptr(addr)

    def fix_zm_palettes(self) -> None:
        if self.settings.rand_enemy or self.settings.rand_tileset:
            # fix kraid's body
            sp_addr = self.get_sprite_addr(0x6F)
            ts_addr = self.get_tileset_addr(9)
            self.rom.copy_bytes(sp_addr, ts_addr + 0x100, 0x20)

        if self.settings.rand_tileset:
            # fix kraid elevator statue
            sp_addr = self.get_sprite_addr(0x95)
            ts_addr = self.get_tileset_addr(0x35)
            self.rom.copy_bytes(ts_addr + 0x20, sp_addr, 0x20)

            # fix ridley elevator statue
            ts_addr = self.get_tileset_addr(7)
            self.rom.copy_bytes(ts_addr + 0x20, sp_addr + 0x20, 0x20)

            # fix tourian statues
            sp_addr = self.get_sprite_addr(0xA3)
            ts_addr = self.get_tileset_addr(0x41)
            self.rom.copy_bytes(ts_addr + 0x60, sp_addr, 0x20)
            # fix cutscene
            sp_addr = self.rom.tourian_statues_cutscene_palette()
            self.rom.copy_bytes(ts_addr, sp_addr, 0xC0)
