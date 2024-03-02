from typing import List, Tuple

from mars_patcher.rom import Game, Region, Rom

# TODO: consider moving these to JSON

def area_room_entry_ptrs(rom: Rom) -> int:
    """Returns the address of the area room entry pointers."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x79B8BC
        elif rom.region == Region.E:
            return 0x79C0F0
        elif rom.region == Region.J:
            return 0x7EDF6C
        elif rom.region == Region.C:
            return 0x77D5C0
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x75FAC4
        elif rom.region == Region.E:
            return 0x773964
        elif rom.region == Region.J:
            return 0x75FBD4
        elif rom.region == Region.C:
            return 0x79ECBC


def tileset_entries(rom: Rom) -> int:
    """Returns the address of the tileset entries."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x3BF888
        elif rom.region == Region.E:
            return 0x3BFEE4
        elif rom.region == Region.J:
            return 0x3C1E50
        elif rom.region == Region.C:
            return 0x3C1E94
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x33DFDC
        elif rom.region == Region.E:
            return 0x33EC68
        elif rom.region == Region.J:
            return 0x33E038
        elif rom.region == Region.C:
            return 0x3577C8


def tileset_count(rom: Rom) -> int:
    """Returns the number of tilesets in the game."""
    if rom.game == Game.MF:
        return 0x62
    elif rom.game == Game.ZM:
        return 0x4F
    raise ValueError(rom.game)


def starting_equipment(rom: Rom) -> int:
    """Returns the address of the starting equipment data."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x28D2AC
        elif rom.region == Region.E:
            return 0x28D908
        elif rom.region == Region.J:
            return 0x28F5B4
        elif rom.region == Region.C:
            return 0x28F5F8
    raise NotImplementedError(rom.game)


def anim_palette_entries(rom: Rom) -> int:
    """Returns the address of the animated palette entries."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x3E3764
        elif rom.region == Region.E:
            return 0x3E3DC0
        elif rom.region == Region.J:
            return 0x3E5D38
        elif rom.region == Region.C:
            return 0x3E5D7C
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x35FBFC
        elif rom.region == Region.E:
            return 0x360888
        elif rom.region == Region.J:
            return 0x35FC58
        elif rom.region == Region.C:
            return 0x3793E8


def anim_palette_count(rom: Rom) -> int:
    """Returns the number of animated palettes in the game."""
    if rom.game == Game.MF:
        if rom.region == Region.U or rom.region == Region.E:
            return 0x21
        elif rom.region == Region.J or rom.region == Region.C:
            return 0x22
    elif rom.game == Game.ZM:
        return 0x12
    raise ValueError(rom.game, rom.region)


def sprite_vram_sizes(rom: Rom) -> int:
    """Returns the address of the sprite VRAM sizes."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x2E4A50
        elif rom.region == Region.E:
            return 0x2E50AC
        elif rom.region == Region.J:
            return 0x2E6D58
        elif rom.region == Region.C:
            return 0x2E6D9C
    raise NotImplementedError(rom.game)


def sprite_graphics_ptrs(rom: Rom) -> int:
    """Returns the address of the sprite graphics pointers."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x79A5D8
        elif rom.region == Region.E:
            return 0x79AE0C
        elif rom.region == Region.J:
            return 0x7ECC88
        elif rom.region == Region.C:
            return 0x77C2DC
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x75EBF8
        elif rom.region == Region.E:
            return 0x772A98
        elif rom.region == Region.J:
            return 0x75ED08
        elif rom.region == Region.C:
            return 0x79DDF0
    raise ValueError(rom.game, rom.region)


def sprite_palette_ptrs(rom: Rom) -> int:
    """Returns the address of the sprite palette pointers."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x79A8D4
        elif rom.region == Region.E:
            return 0x79B108
        elif rom.region == Region.J:
            return 0x7ECF84
        elif rom.region == Region.C:
            return 0x77C5D8
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x75EEF0
        elif rom.region == Region.E:
            return 0x772D90
        elif rom.region == Region.J:
            return 0x75F000
        elif rom.region == Region.C:
            return 0x79E0E8
    raise ValueError(rom.game, rom.region)


def sprite_count(rom: Rom) -> int:
    """Returns the number of sprites in the game."""
    if rom.game == Game.MF:
        return 0xCF
    elif rom.game == Game.ZM:
        return 0xCE
    raise ValueError(rom.game)


def spriteset_ptrs(rom: Rom) -> int:
    """Returns the address of the spriteset pointers."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x79ADD8
        elif rom.region == Region.E:
            return 0x79B60C
        elif rom.region == Region.J:
            return 0x7ED488
        elif rom.region == Region.C:
            return 0x77CADC
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x75F31C
        elif rom.region == Region.E:
            return 0x7731BC
        elif rom.region == Region.J:
            return 0x75F42C
        elif rom.region == Region.C:
            return 0x79E514
    raise ValueError(rom.game, rom.region)


def spriteset_count(rom: Rom) -> int:
    """Returns the number of spritesets in the game."""
    if rom.game == Game.MF:
        return 0x82
    elif rom.game == Game.ZM:
        return 0x72
    raise ValueError(rom.game)


def samus_palettes(rom: Rom) -> List[Tuple[int, int]]:
    """Returns a list of (address, row count) pairs."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return [(0x28DD7C, 0x5E), (0x28EAFC, 0x70)]
        elif rom.region == Region.E:
            return [(0x28E3D8, 0x5E), (0x28F158, 0x70)]
        elif rom.region == Region.J:
            return [(0x290084, 0x5E), (0x290E04, 0x70)]
        elif rom.region == Region.C:
            return [(0x2900C8, 0x5E), (0x290E48, 0x70)]
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return [(0x2376A8, 0xA3)]
        elif rom.region == Region.E:
            return [(0x238334, 0xA3)]
        elif rom.region == Region.J:
            return [(0x237704, 0xA3)]
        elif rom.region == Region.C:
            return [(0x250E94, 0xA3)]
    raise ValueError(rom.game, rom.region)


def file_select_helmet_palettes(rom: Rom) -> List[Tuple[int, int]]:
    """Returns a list of (address, row count) pairs."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return [(0x740E08, 0x1), (0x740EA8, 0x2)]
        elif rom.region == Region.E:
            return [(0x741618, 0x1), (0x7416B8, 0x2)]
        elif rom.region == Region.J:
            return [(0x73FCDC, 0x1), (0x73FD7C, 0x2)]
        elif rom.region == Region.C:
            return [(0x6CE360, 0x1), (0x6CE400, 0x2)]
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return [(0x454938, 0x1), (0x4549B8, 0x1)]
        elif rom.region == Region.E:
            return [(0x4603F8, 0x1), (0x460478, 0x1)]
        elif rom.region == Region.J:
            return [(0x454994, 0x1), (0x454A14, 0x1)]
        elif rom.region == Region.C:
            return [(0x4768FC, 0x1), (0x47697C, 0x1)]
    raise ValueError(rom.game, rom.region)


def beam_palettes(rom: Rom) -> List[Tuple[int, int]]:
    """Returns a list of (address, row count) pairs."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return [(0x58B464, 0x6)]
        elif rom.region == Region.E:
            return [(0x58BAC0, 0x6)]
        elif rom.region == Region.J:
            return [(0x58BBF4, 0x6)]
        elif rom.region == Region.C:
            return [(0x592578, 0x6)]
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return [(0x3270E8, 0x6)]
        elif rom.region == Region.E:
            return [(0x327D74, 0x6)]
        elif rom.region == Region.J:
            return [(0x327144, 0x6)]
        elif rom.region == Region.C:
            return [(0x3408D4, 0x6)]
    raise ValueError(rom.game, rom.region)


def tourian_statues_cutscene_palette(rom: Rom) -> int:
    """Returns the address of the palette used for the Tourian statue cutscenes."""
    if rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x3ED53C
        elif rom.region == Region.E:
            return 0x3EE1C8
        elif rom.region == Region.J:
            return 0x3ED598
        elif rom.region == Region.C:
            return 0x406D28
    raise ValueError(rom.game)


def file_screen_text_ptrs(rom: Rom) -> int:
    """Returns the address of the file screen text pointers."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x79EC68
        elif rom.region == Region.E:
            return 0x79F4C4
        elif rom.region == Region.J:
            return 0x7F13FC
    raise ValueError(rom.game)


def character_widths(rom: Rom) -> int:
    """Returns the address of the character widths."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x576234
        elif rom.region == Region.E:
            return 0x576890
        elif rom.region == Region.J:
            return 0x578934
        elif rom.region == Region.C:
            return 0x57D21C
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x40D7B0
        elif rom.region == Region.E:
            return 0x40E5E4
        elif rom.region == Region.J:
            return 0x40D80C
        elif rom.region == Region.C:
            return 0x42F34C
    raise ValueError(rom.game, rom.region)


def navigation_text_ptrs(rom: Rom) -> int:
    """Returns the address of the navigation text pointers."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x79C0F0
        elif rom.region == Region.E:
            return 0x79C924
        elif rom.region == Region.J:
            return 0x7EE7A0
        elif rom.region == Region.C:
            return 0x77DDF4
    raise ValueError(rom.game)
