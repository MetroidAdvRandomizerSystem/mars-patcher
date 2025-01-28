import random
from enum import Enum

import mars_patcher.constants.game_data as gd
from mars_patcher.auto_generated_types import (
    MarsschemaPalettes,
    MarsschemaPalettesColorspace,
    MarsschemaPalettesRandomize,
)
from mars_patcher.constants.palettes import (
    ENEMY_GROUPS,
    EXCLUDED_ENEMIES,
    MF_TILESET_ALT_PAL_ROWS,
    TILESET_ANIM_PALS,
)
from mars_patcher.palette import Palette
from mars_patcher.rom import Game, Rom


class PaletteType(Enum):
    TILESETS = 1
    ENEMIES = 2
    SAMUS = 3
    BEAMS = 4


class PaletteSettings:
    PAL_TYPE_ENUMS = {
        "Tilesets": PaletteType.TILESETS,
        "Enemies": PaletteType.ENEMIES,
        "Samus": PaletteType.SAMUS,
        "Beams": PaletteType.BEAMS,
    }

    def __init__(
        self,
        seed: int,
        pal_types: dict[PaletteType, tuple[int, int]],  # TODO: change this tuple(int, int)
        color_space: MarsschemaPalettesColorspace,
        symmetric: bool,
    ):
        self.seed = seed
        self.pal_types = pal_types
        self.color_space: MarsschemaPalettesColorspace = color_space
        self.symmetric = symmetric

    @classmethod
    def from_json(cls, data: MarsschemaPalettes) -> "PaletteSettings":
        seed = data.get("Seed", random.randint(0, 2**31 - 1))
        random.seed(seed)
        pal_types = {}
        for type_name, hue_data in data["Randomize"].items():
            pal_type = cls.PAL_TYPE_ENUMS[type_name]
            hue_range = cls.get_hue_range(hue_data)
            pal_types[pal_type] = hue_range
        color_space = data.get("ColorSpace", "Oklab")
        symmetric = data.get("Symmetric", True)
        return cls(seed, pal_types, color_space, symmetric)

    @classmethod
    def get_hue_range(cls, data: MarsschemaPalettesRandomize) -> tuple[int, int]:
        hue_min = data.get("HueMin")
        hue_max = data.get("HueMax")
        if hue_min is None or hue_max is None:
            if hue_max is not None:
                hue_min = random.randint(0, hue_max)
            elif hue_min is not None:
                hue_max = random.randint(hue_min, 360)
            else:
                hue_min = random.randint(0, 360)
                hue_max = random.randint(hue_min, 360)
        if hue_min > hue_max:
            raise ValueError("HueMin cannot be greater than HueMax")
        return hue_min, hue_max


class PaletteRandomizer:
    """Class for randomly shifting the hues of color palettes."""

    def __init__(self, rom: Rom, settings: PaletteSettings):
        self.rom = rom
        self.settings = settings
        if settings.color_space == "HSV":
            self.shift_func = self.shift_palette_hsv
        elif settings.color_space == "Oklab":
            self.shift_func = self.shift_palette_oklab
        else:
            raise ValueError(f"Invalid color space '{settings.color_space}' for color space!")

    @staticmethod
    def shift_palette_hsv(pal: Palette, shift: int, excluded_rows: set[int] = set()) -> None:
        pal.shift_hue_hsv(shift, excluded_rows)

    @staticmethod
    def shift_palette_oklab(pal: Palette, shift: int, excluded_rows: set[int] = set()) -> None:
        pal.shift_hue_oklab(shift, excluded_rows)

    def get_hue_shift(self, hue_range: tuple[int, int]) -> int:
        """Returns a hue shift in a random direction between hue_min and hue_max."""
        shift = random.randint(hue_range[0], hue_range[1])
        if self.settings.symmetric and random.random() < 0.5:
            shift = 360 - shift
        return shift

    def randomize(self) -> None:
        random.seed(self.settings.seed)
        self.randomized_pals: set[int] = set()
        pal_types = self.settings.pal_types
        if PaletteType.TILESETS in pal_types:
            self.randomize_tilesets(pal_types[PaletteType.TILESETS])
        if PaletteType.ENEMIES in pal_types:
            self.randomize_enemies(pal_types[PaletteType.ENEMIES])
        if PaletteType.SAMUS in pal_types:
            self.randomize_samus(pal_types[PaletteType.SAMUS])
        if PaletteType.BEAMS in pal_types:
            self.randomize_beams(pal_types[PaletteType.BEAMS])
        # Fix any sprite/tileset palettes that should be the same
        # TODO: Check for palette fixes needed in fusion
        if self.rom.is_zm():
            self.fix_zm_palettes()

    def shift_palettes(self, pals: list[tuple[int, int]], shift: int) -> None:
        for addr, rows in pals:
            if addr in self.randomized_pals:
                continue
            pal = Palette(rows, self.rom, addr)
            self.shift_func(pal, shift)
            pal.write(self.rom, addr)
            self.randomized_pals.add(addr)

    def randomize_samus(self, hue_range: tuple[int, int]) -> None:
        shift = self.get_hue_shift(hue_range)
        self.shift_palettes(gd.samus_palettes(self.rom), shift)
        self.shift_palettes(gd.helmet_cursor_palettes(self.rom), shift)
        self.shift_palettes(gd.sax_palettes(self.rom), shift)

    def randomize_beams(self, hue_range: tuple[int, int]) -> None:
        shift = self.get_hue_shift(hue_range)
        self.shift_palettes(gd.beam_palettes(self.rom), shift)

    def randomize_tilesets(self, hue_range: tuple[int, int]) -> None:
        rom = self.rom
        ts_addr = gd.tileset_entries(rom)
        ts_count = gd.tileset_count(rom)
        anim_pal_count = gd.anim_palette_count(rom)
        anim_pal_to_randomize = set(range(anim_pal_count))

        for _ in range(ts_count):
            # Get tileset palette address
            pal_ptr = ts_addr + 4
            pal_addr = rom.read_ptr(pal_ptr)
            ts_addr += 0x14
            if pal_addr in self.randomized_pals:
                continue
            # Get excluded palette rows
            excluded_rows = set()
            if rom.game == Game.MF:
                row = MF_TILESET_ALT_PAL_ROWS.get(pal_addr)
                if row is not None:
                    excluded_rows = {row}
            # Load palette and shift hue
            pal = Palette(13, rom, pal_addr)
            shift = self.get_hue_shift(hue_range)
            self.shift_func(pal, shift, excluded_rows)
            pal.write(rom, pal_addr)
            self.randomized_pals.add(pal_addr)
            # Check animated palette
            anim_pal_id = TILESET_ANIM_PALS.get(pal_addr)
            if anim_pal_id is not None:
                self.randomize_anim_palette(anim_pal_id, shift)
                anim_pal_to_randomize.remove(anim_pal_id)

        # Go through remaining animated palettes
        for anim_pal_id in anim_pal_to_randomize:
            shift = self.get_hue_shift(hue_range)
            self.randomize_anim_palette(anim_pal_id, shift)

    def randomize_anim_palette(self, anim_pal_id: int, shift: int) -> None:
        rom = self.rom
        addr = gd.anim_palette_entries(rom) + anim_pal_id * 8
        pal_addr = rom.read_ptr(addr + 4)
        if pal_addr in self.randomized_pals:
            return
        rows = rom.read_8(addr + 2)
        pal = Palette(rows, rom, pal_addr)
        self.shift_func(pal, shift)
        pal.write(rom, pal_addr)
        self.randomized_pals.add(pal_addr)

    def randomize_enemies(self, hue_range: tuple[int, int]) -> None:
        rom = self.rom
        excluded = EXCLUDED_ENEMIES[rom.game]
        sp_count = gd.sprite_count(rom)
        to_randomize = set(range(0x10, sp_count))
        to_randomize -= excluded

        # Go through sprites in groups
        groups = ENEMY_GROUPS[rom.game]
        for _, sprite_ids in groups.items():
            shift = self.get_hue_shift(hue_range)
            for sprite_id in sprite_ids:
                assert sprite_id in to_randomize, f"{sprite_id:X} should be excluded"
                self.randomize_enemy(sprite_id, shift)
                to_randomize.remove(sprite_id)

        # Go through remaining sprites
        for sprite_id in to_randomize:
            shift = self.get_hue_shift(hue_range)
            self.randomize_enemy(sprite_id, shift)

    def randomize_enemy(self, sprite_id: int, shift: int) -> None:
        rom = self.rom
        sprite_gfx_id = sprite_id - 0x10
        pal_ptr = gd.sprite_palette_ptrs(rom)
        pal_addr = rom.read_ptr(pal_ptr + sprite_gfx_id * 4)
        if pal_addr in self.randomized_pals:
            return
        if rom.is_mf():
            if sprite_id == 0x4D or sprite_id == 0xBE:
                # Ice beam ability and zozoros only have 1 row, not 2
                rows = 1
            else:
                vram_size_addr = gd.sprite_vram_sizes(rom)
                vram_size = rom.read_32(vram_size_addr + sprite_gfx_id * 4)
                rows = vram_size // 0x800
        elif rom.is_zm():
            gfx_ptr = gd.sprite_graphics_ptrs(rom)
            gfx_addr = rom.read_ptr(gfx_ptr + sprite_gfx_id * 4)
            rows = (rom.read_32(gfx_addr) >> 8) // 0x800
        pal = Palette(rows, rom, pal_addr)
        self.shift_func(pal, shift)
        pal.write(rom, pal_addr)
        self.randomized_pals.add(pal_addr)

    def get_sprite_addr(self, sprite_id: int) -> int:
        addr = gd.sprite_palette_ptrs(self.rom) + (sprite_id - 0x10) * 4
        return self.rom.read_ptr(addr)

    def get_tileset_addr(self, sprite_id: int) -> int:
        addr = gd.tileset_entries(self.rom) + sprite_id * 0x14 + 4
        return self.rom.read_ptr(addr)

    def fix_zm_palettes(self) -> None:
        if (
            PaletteType.ENEMIES in self.settings.pal_types
            or PaletteType.TILESETS in self.settings.pal_types
        ):
            # Fix kraid's body
            sp_addr = self.get_sprite_addr(0x6F)
            ts_addr = self.get_tileset_addr(9)
            self.rom.copy_bytes(sp_addr, ts_addr + 0x100, 0x20)

        if PaletteType.TILESETS in self.settings.pal_types:
            # Fix kraid elevator statue
            sp_addr = self.get_sprite_addr(0x95)
            ts_addr = self.get_tileset_addr(0x35)
            self.rom.copy_bytes(ts_addr + 0x20, sp_addr, 0x20)

            # Fix ridley elevator statue
            ts_addr = self.get_tileset_addr(7)
            self.rom.copy_bytes(ts_addr + 0x20, sp_addr + 0x20, 0x20)

            # Fix tourian statues
            sp_addr = self.get_sprite_addr(0xA3)
            ts_addr = self.get_tileset_addr(0x41)
            self.rom.copy_bytes(ts_addr + 0x60, sp_addr, 0x20)
            # Fix cutscene
            sp_addr = gd.tourian_statues_cutscene_palette(self.rom)
            self.rom.copy_bytes(ts_addr, sp_addr, 0xC0)
