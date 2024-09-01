from typing import Dict, Tuple

from mars_patcher.constants.game_data import area_doors_ptrs, spriteset_ptrs, starting_equipment
from mars_patcher.constants.items import BEAM_FLAGS, MISSILE_BOMB_FLAGS, SUIT_MISC_FLAGS
from mars_patcher.rom import Rom
from mars_patcher.room_entry import RoomEntry
from mars_patcher.constants.reserved_space import ReservedConstants

# keep in sync with base patch
STARTING_LOC_ADDR = ReservedConstants.STARTING_LOCATION_ADDR


def set_starting_location(rom: Rom, data: Dict) -> None:
    area = data["Area"]
    room = data["Room"]
    # don't do anything for area 0 room 0
    if area == 0 and room == 0:
        return
    # find any door in the provided room
    door = find_door_in_room(rom, area, room)
    # check if save pad in room
    pos = find_save_pad_position(rom, area, room)
    if pos is not None:
        x_pos, y_pos = pos
    else:
        # convert block coordinates to actual position
        x_pos = data["BlockX"] * 64 + 31
        y_pos = data["BlockY"] * 64 + 63
    # write to rom
    rom.write_8(STARTING_LOC_ADDR, area)
    rom.write_8(STARTING_LOC_ADDR + 1, room)
    rom.write_8(STARTING_LOC_ADDR + 2, door)
    rom.write_16(STARTING_LOC_ADDR + 4, x_pos)
    rom.write_16(STARTING_LOC_ADDR + 6, y_pos)


def find_door_in_room(rom: Rom, area: int, room: int) -> int:
    door_addr = rom.read_ptr(area_doors_ptrs(rom) + area * 4)
    door = None
    for d in range(256):
        if rom.read_8(door_addr) == 0:
            break
        if rom.read_8(door_addr + 1) == room:
            door = d
            break
        door_addr += 0xC
    if door is None:
        raise ValueError(f"No door found for area {area} room {room:X}")
    return door


def find_save_pad_position(rom: Rom, area: int, room: int) -> Tuple[int, int] | None:
    # check if room's spriteset has save pad
    room_entry = RoomEntry(rom, area, room)
    spriteset = room_entry.default_spriteset()
    ss_addr = rom.read_ptr(spriteset_ptrs(rom) + spriteset * 4)
    ss_idx = None
    for i in range(15):
        sprite_id = rom.read_8(ss_addr)
        if sprite_id == 0:
            break
        if sprite_id == 0x1F:
            ss_idx = i
            break
        ss_addr += 2
    if ss_idx is None:
        return None
    # find save pad in sprite layout list
    layout_addr = room_entry.default_sprite_layout_addr()
    for i in range(24):
        sp_y = rom.read_8(layout_addr)
        sp_x = rom.read_8(layout_addr + 1)
        prop = rom.read_8(layout_addr + 2)
        if sp_x == 0xFF and sp_y == 0xFF and prop == 0xFF:
            break
        if (prop & 0xF) - 1 == ss_idx:
            x_pos = sp_x * 64 + 32
            y_pos = sp_y * 64 + 9
            return x_pos, y_pos
        layout_addr += 3
    # no save pad found
    return None


def set_starting_items(rom: Rom, data: Dict) -> None:
    def get_ability_flags(ability_flags: Dict[str, int]) -> int:
        status = 0
        for ability, flag in ability_flags.items():
            if ability in abilities:
                status |= flag
        return status

    # get health/ammo amounts
    energy = data.get("Energy", 99)
    missiles = data.get("Missiles", 10)
    power_bombs = data.get("PowerBombs", 10)
    # get ability status flags
    abilities = data.get("Abilities", [])
    beam_status = get_ability_flags(BEAM_FLAGS)
    missile_bomb_status = get_ability_flags(MISSILE_BOMB_FLAGS)
    suit_misc_status = get_ability_flags(SUIT_MISC_FLAGS)
    # get security level flags
    levels = data.get("SecurityLevels", [0])
    level_status = 0
    for level in levels:
        level_status |= 1 << level
    # get downloaded map flags
    maps = data.get("DownloadedMaps", range(7))
    map_status = 0
    for map in maps:
        map_status |= 1 << map
    # write to rom
    addr = starting_equipment(rom)
    rom.write_16(addr, energy)
    rom.write_16(addr + 2, energy)
    rom.write_16(addr + 4, missiles)
    rom.write_16(addr + 6, missiles)
    rom.write_8(addr + 8, power_bombs)
    rom.write_8(addr + 9, power_bombs)
    rom.write_8(addr + 0xA, beam_status)
    rom.write_8(addr + 0xB, missile_bomb_status)
    rom.write_8(addr + 0xC, suit_misc_status)
    rom.write_8(addr + 0xD, level_status)
    rom.write_8(addr + 0xE, map_status)
