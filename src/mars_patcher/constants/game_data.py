from typing import List, Tuple

from mars_patcher.rom import Game, Region, Rom

# TODO: Consider moving these to JSON


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

    raise ValueError("Rom has unknown game loaded.")


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

    raise ValueError("Rom has unknown game loaded.")


def tileset_count(rom: Rom) -> int:
    """Returns the number of tilesets in the game."""
    if rom.game == Game.MF:
        return 0x62
    elif rom.game == Game.ZM:
        return 0x4F
    raise ValueError(rom.game)


def area_doors_ptrs(rom: Rom) -> int:
    """Returns the address of the area doors pointers."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x79B894
        elif rom.region == Region.E:
            return 0x79C0C8
        elif rom.region == Region.J:
            return 0x7EDF44
        elif rom.region == Region.C:
            return 0x77D598
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x75FAA8
        elif rom.region == Region.E:
            return 0x773948
        elif rom.region == Region.J:
            return 0x75FBB8
        elif rom.region == Region.C:
            return 0x79ECA0

    raise ValueError("Rom has unknown game loaded.")


def area_connections(rom: Rom) -> int:
    """Returns the address of the area connections list."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x3C8B90
        elif rom.region == Region.E:
            return 0x3C91EC
        elif rom.region == Region.J:
            return 0x3CB158
        elif rom.region == Region.C:
            return 0x3CB19C
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x360274
        elif rom.region == Region.E:
            return 0x360F00
        elif rom.region == Region.J:
            return 0x3602D0
        elif rom.region == Region.C:
            return 0x379A60

    raise ValueError("Rom has unknown game loaded.")


def area_connections_count(rom: Rom) -> int:
    """Returns the number of area connections in the game. Excludes the final entry of FFs."""
    if rom.game == Game.MF:
        return 0x22
    elif rom.game == Game.ZM:
        return 0x19

    raise ValueError("Rom has unknown game loaded.")


def hatch_lock_events(rom: Rom) -> int:
    """Returns the address of the hatch lock events."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x3C8A5C
        elif rom.region == Region.E:
            return 0x3C90B8
        elif rom.region == Region.J:
            return 0x3CB024
        elif rom.region == Region.C:
            return 0x3CB068
    raise ValueError(rom.game)


def hatch_lock_event_count(rom: Rom) -> int:
    """Returns the number of hatch lock events in the game."""
    if rom.game == Game.MF:
        return 0x4B
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

    raise ValueError("Rom has unknown game loaded.")


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
    raise ValueError(rom.game)


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
    """Returns a list of (address, row count) pairs for all of Samus's palettes."""
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


def helmet_cursor_palettes(rom: Rom) -> List[Tuple[int, int]]:
    """
    Returns a list of (address, row count) pairs for Samus's helmet as a cursor
    (file select and game over)
    """
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return [(0x740E08, 1), (0x740EA8, 2), (0x73C544, 1), (0x73C584, 2)]
        elif rom.region == Region.E:
            return [(0x741618, 1), (0x7416B8, 2), (0x73CD54, 1), (0x73CD94, 2)]
        elif rom.region == Region.J:
            return [(0x73FCDC, 1), (0x73FD7C, 2), (0x73C030, 1), (0x73C070, 2)]
        elif rom.region == Region.C:
            return [(0x6CE360, 1), (0x6CE400, 2), (0x6CA8F8, 1), (0x6CA938, 2)]
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return [(0x454938, 1), (0x4549B8, 1)]
        elif rom.region == Region.E:
            return [(0x4603F8, 1), (0x460478, 1)]
        elif rom.region == Region.J:
            return [(0x454994, 1), (0x454A14, 1)]
        elif rom.region == Region.C:
            return [(0x4768FC, 1), (0x47697C, 1)]
    raise ValueError(rom.game, rom.region)


def beam_palettes(rom: Rom) -> List[Tuple[int, int]]:
    """Returns a list of (address, row count) pairs for beam palettes."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return [(0x58B464, 6)]
        elif rom.region == Region.E:
            return [(0x58BAC0, 6)]
        elif rom.region == Region.J:
            return [(0x58BBF4, 6)]
        elif rom.region == Region.C:
            return [(0x592578, 6)]
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return [(0x3270E8, 6)]
        elif rom.region == Region.E:
            return [(0x327D74, 6)]
        elif rom.region == Region.J:
            return [(0x327144, 6)]
        elif rom.region == Region.C:
            return [(0x3408D4, 6)]
    raise ValueError(rom.game, rom.region)


def sax_palettes(rom: Rom) -> List[Tuple[int, int]]:
    """Returns a list of (address, row count) pairs for all of the SA-X's palettes."""
    if rom.game == Game.MF:
        # Normal, Lab, Monster, Extra
        if rom.region == Region.U:
            return [(0x2E7D60, 2), (0x2E91D8, 2), (0x38CFB4, 8), (0x2B4368, 5)]
        elif rom.region == Region.E:
            return [(0x2E83BC, 2), (0x2E9834, 2), (0x38D610, 8), (0x2B49C4, 5)]
        elif rom.region == Region.J:
            return [(0x2EA068, 2), (0x2EB4E0, 2), (0x38F2BC, 8), (0x2B6670, 5)]
        elif rom.region == Region.C:
            return [(0x2EA0AC, 2), (0x2EB524, 2), (0x38F300, 8), (0x2B66B4, 5)]
    raise ValueError(rom.game)


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


def sound_data_entries(rom: Rom) -> int:
    """Returns the address of the sound data entries."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0xA8D3C
        elif rom.region == Region.E:
            return 0xA9398
        elif rom.region == Region.J:
            return 0xAB0A0
        elif rom.region == Region.C:
            return 0xAB0E4
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x8F2C0
        elif rom.region == Region.E:
            return 0x8FF4C
        elif rom.region == Region.J:
            return 0x8F31C
        elif rom.region == Region.C:
            return 0xA8AAC
    raise ValueError(rom.game, rom.region)


def sound_count(rom: Rom) -> int:
    """Returns the number of sounds in the game."""
    if rom.game == Game.MF:
        return 0x2E9
    elif rom.game == Game.ZM:
        return 0x2C4
    raise ValueError(rom.game)


def minimap_ptrs(rom: Rom) -> int:
    """Returns the address of the minimap data pointers."""
    if rom.game == Game.MF:
        if rom.region == Region.U:
            return 0x79BE5C
        elif rom.region == Region.E:
            return 0x79C690
        elif rom.region == Region.J:
            return 0x7EE50C
        elif rom.region == Region.C:
            return 0x77DB60
    elif rom.game == Game.ZM:
        if rom.region == Region.U:
            return 0x7601EC
        elif rom.region == Region.E:
            return 0x77408C
        elif rom.region == Region.J:
            return 0x7602FC
        elif rom.region == Region.C:
            return 0x79F3EC
    raise ValueError(rom.game, rom.region)


def minimap_count(rom: Rom) -> int:
    """Returns the number of minimaps in the game."""
    if rom.game == Game.MF:
        return 11
    elif rom.game == Game.ZM:
        return 11
    raise ValueError(rom.game)
