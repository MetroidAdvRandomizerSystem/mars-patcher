from enum import Enum

from mars_patcher.auto_generated_types import MarsschemaDoorlocksItem
from mars_patcher.constants.game_data import (
    area_doors_ptrs,
    hatch_lock_event_count,
    hatch_lock_events,
    minimap_count,
)
from mars_patcher.constants.minimap_tiles import COLORED_DOOR_TILES, NORMAL_DOOR_TILES
from mars_patcher.minimap import MINIMAP_DIM, Minimap
from mars_patcher.rom import Rom
from mars_patcher.room_entry import BlockLayer, RoomEntry


class HatchLock(Enum):
    OPEN = 0
    LEVEL_0 = 1
    LEVEL_1 = 2
    LEVEL_2 = 3
    LEVEL_3 = 4
    LEVEL_4 = 5
    LOCKED = 6


HATCH_LOCK_ENUMS = {
    "Open": HatchLock.OPEN,
    "Level0": HatchLock.LEVEL_0,
    "Level1": HatchLock.LEVEL_1,
    "Level2": HatchLock.LEVEL_2,
    "Level3": HatchLock.LEVEL_3,
    "Level4": HatchLock.LEVEL_4,
    "Locked": HatchLock.LOCKED,
}

BG1_VALUES = {
    HatchLock.OPEN: 0x4,
    HatchLock.LEVEL_0: 0x6,
    HatchLock.LEVEL_1: 0x8,
    HatchLock.LEVEL_2: 0xA,
    HatchLock.LEVEL_3: 0xC,
    HatchLock.LEVEL_4: 0xE,
    HatchLock.LOCKED: 0x819A,
}

CLIP_VALUES = {
    HatchLock.OPEN: [0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    HatchLock.LEVEL_0: [0x30, 0x31, 0x32, 0x33, 0x34, 0x35],
    HatchLock.LEVEL_1: [0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B],
    HatchLock.LEVEL_2: [0x40, 0x41, 0x42, 0x43, 0x44, 0x45],
    HatchLock.LEVEL_3: [0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B],
    HatchLock.LEVEL_4: [0x3C, 0x3D, 0x3E, 0x4C, 0x4D, 0x4E],
    HatchLock.LOCKED: [0x10, 0x10, 0x10, 0x10, 0x10, 0x10],
}

CLIP_TO_HATCH_LOCK: dict[int, HatchLock] = {}
for lock, vals in CLIP_VALUES.items():
    for val in vals:
        CLIP_TO_HATCH_LOCK[val] = lock

EXCLUDED_DOORS = {
    (0, 0xB4),  # Restricted lab escape
}


# TODO:
# - Optimize by only loading rooms that contain doors to modify
# - Split into more than one function for readability
def set_door_locks(rom: Rom, data: list[MarsschemaDoorlocksItem]) -> None:
    door_locks = parse_door_lock_data(data)
    # Go through all doors in game in order
    doors_ptrs = area_doors_ptrs(rom)
    loaded_rooms: dict[tuple[int, int], RoomEntry] = {}
    # (AreaID, RoomID): (BG1, Clipdata)
    loaded_bg1_and_clip: dict[tuple[int, int], tuple[BlockLayer, BlockLayer]] = {}
    # (AreaID, RoomID): (CappedSlot, CaplessSlot)
    orig_room_hatch_slots: dict[tuple[int, int], tuple[int, int]] = {}
    new_room_hatch_slots: dict[tuple[int, int], tuple[int, int]] = {}
    # (AreaID, RoomID): {OrigSlot: NewSlot}
    hatch_slot_changes: dict[tuple[int, int], dict[int, int]] = {}
    for area in range(7):
        area_addr = rom.read_ptr(doors_ptrs + area * 4)
        for door in range(256):
            door_addr = area_addr + door * 0xC
            door_type = rom.read_8(door_addr)
            # Check if at end of list
            if door_type == 0:
                break
            # Skip doors that mage marks as deleted
            room = rom.read_8(door_addr + 1)
            if room == 0xFF:
                continue
            # Skip excluded doors and doors that aren't lockable hatches
            lock = door_locks.get((area, door))
            if (area, door) in EXCLUDED_DOORS or door_type & 0xF != 4:
                assert lock is None, f"Area {area} door {door} cannot have its lock changed"
                continue
            # Load room's BG1 and clipdata if not already loaded
            area_room = (area, room)
            room_entry = loaded_rooms.get(area_room)
            if room_entry is None:
                room_entry = RoomEntry(rom, area, room)
                bg1 = room_entry.load_bg1()
                clip = room_entry.load_clip()
                loaded_rooms[area_room] = room_entry
                loaded_bg1_and_clip[area_room] = (bg1, clip)
                orig_room_hatch_slots[area_room] = (0, 5)
                new_room_hatch_slots[area_room] = (0, 5)
                hatch_slot_changes[area_room] = {}
            else:
                _tuple = loaded_bg1_and_clip.get(area_room)
                if _tuple is not None:
                    bg1, clip = _tuple

            # Check x exit distance to get facing direction
            x_exit = rom.read_8(door_addr + 7)
            facing_right = x_exit < 0x80
            dx = 1 if facing_right else -1
            # Get hatch position
            hatch_x = rom.read_8(door_addr + 2) + dx
            hatch_y = rom.read_8(door_addr + 4)
            # Get original hatch slot number
            capped_slot, capless_slot = orig_room_hatch_slots[area_room]
            clip_val = clip.get_block_value(hatch_x, hatch_y)
            orig_has_cap = clip_val != 0
            if orig_has_cap:
                # Has cap
                orig_hatch_slot = capped_slot
                capped_slot += 1
            else:
                # Capless
                orig_hatch_slot = capless_slot
                capless_slot -= 1
            orig_room_hatch_slots[area_room] = (capped_slot, capless_slot)
            # Get new hatch slot number
            capped_slot, capless_slot = new_room_hatch_slots[area_room]
            if (lock is None and orig_has_cap) or (lock is not None and lock != HatchLock.OPEN):
                # Has cap
                new_hatch_slot = capped_slot
                capped_slot += 1
            else:
                # Capless
                new_hatch_slot = capless_slot
                capless_slot -= 1
            new_room_hatch_slots[area_room] = (capped_slot, capless_slot)
            if new_hatch_slot != orig_hatch_slot:
                hatch_slot_changes[area_room][orig_hatch_slot] = new_hatch_slot
            # Overwrite BG1 and clipdata
            if lock is None:
                # Even if a hatch's lock hasn't changed, its slot may have changed
                lock = CLIP_TO_HATCH_LOCK.get(clip_val)
                if lock is None:
                    continue
            bg1_val = BG1_VALUES[lock]
            if facing_right:
                bg1_val += 1
            clip_val = CLIP_VALUES[lock][new_hatch_slot]
            for y in range(4):
                bg1.set_block_value(hatch_x, hatch_y + y, bg1_val)
                clip.set_block_value(hatch_x, hatch_y + y, clip_val)
                bg1_val += 0x10
    # Write BG1 and clipdata for each room
    for bg1, clip in loaded_bg1_and_clip.values():
        bg1.write()
        clip.write()
    fix_hatch_lock_events(rom, hatch_slot_changes)


def remove_door_colors_on_minimap(rom: Rom) -> None:
    for id in range(minimap_count(rom)):
        with Minimap(rom, id) as minimap:
            for y in range(MINIMAP_DIM):
                for x in range(MINIMAP_DIM):
                    tile, pal, h_flip, v_flip = minimap.get_tile_value(x, y)
                    tile_type = COLORED_DOOR_TILES.get(tile)
                    if tile_type is not None:
                        tile = NORMAL_DOOR_TILES[tile_type]
                        minimap.set_tile_value(x, y, tile, pal, h_flip, v_flip)


def parse_door_lock_data(data: list[MarsschemaDoorlocksItem]) -> dict[tuple[int, int], HatchLock]:
    """Returns a dictionary of `(AreaID, RoomID): HatchLock` from the input data."""
    door_locks: dict[tuple[int, int], HatchLock] = {}
    for entry in data:
        area_door = (entry["Area"], entry["Door"])
        lock = HATCH_LOCK_ENUMS[entry["LockType"]]
        door_locks[area_door] = lock
    return door_locks


def fix_hatch_lock_events(
    rom: Rom, hatch_slot_changes: dict[tuple[int, int], dict[int, int]]
) -> None:
    hatch_locks_addr = hatch_lock_events(rom)
    count = hatch_lock_event_count(rom)
    for i in range(count):
        addr = hatch_locks_addr + i * 5
        area = rom.read_8(addr + 1)
        room = rom.read_8(addr + 2) - 1
        changes = hatch_slot_changes.get((area, room))
        # Some rooms no longer have doors in rando
        if changes is None:
            continue
        hatch_flags = rom.read_8(addr + 3)
        new_flags = 0
        remain = (1 << 6) - 1
        for prev_slot, new_slot in changes.items():
            if (1 << prev_slot) & hatch_flags != 0:
                new_flags |= 1 << new_slot
            remain &= ~(1 << new_slot)
        new_flags |= hatch_flags & remain
        rom.write_8(addr + 3, new_flags)
