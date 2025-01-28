from mars_patcher.auto_generated_types import MarsschemaTankincrements
from mars_patcher.constants.reserved_space import ReservedConstants
from mars_patcher.locations import ItemSprite, ItemType, LocationSettings
from mars_patcher.rom import Rom
from mars_patcher.room_entry import RoomEntry
from mars_patcher.tileset import Tileset

MINOR_LOCS_TABLE_ADDR = ReservedConstants.MINOR_LOCS_TABLE_ADDR
MINOR_LOCS_ARRAY_ADDR = ReservedConstants.MINOR_LOCS_ARRAY_ADDR
MINOR_LOC_SIZE = 0x8
MAJOR_LOCS_ADDR = ReservedConstants.MAJOR_LOCS_ADDR
MAJOR_LOC_SIZE = 0x2
TANK_INC_ADDR = ReservedConstants.TANK_INC_ADDR
REQUIRED_METROID_COUNT_ADDR = ReservedConstants.REQUIRED_METROID_COUNT_ADDR
TOTAL_METROID_COUNT_ADDR = ReservedConstants.TOTAL_METROID_COUNT_ADDR

TANK_CLIP = (0x62, 0x63, 0x68)
HIDDEN_TANK_CLIP = (0x64, 0x65, 0x69)
TANK_BG1_START = 0x40
TANK_TILE = (0x50, 0x54, 0x58)


class ItemPatcher:
    """Class for writing item assignments to a ROM."""

    def __init__(self, rom: Rom, settings: LocationSettings):
        self.rom = rom
        self.settings = settings

    def _binary_search_rooms_array(self, start_address: int, room: int) -> int:
        """Returns either the address of the room, or -1 if the room was not found."""
        low_end = 0
        high_end = 16
        while low_end < high_end:
            middle = (low_end + high_end) // 2
            read_value = self.rom.read_8(start_address + middle)
            if read_value < room:
                low_end = middle + 1
            elif read_value > room:
                high_end = middle
            else:
                return start_address + middle

        return -1

    # TODO: Use separate classes for handling tilesets and backgrounds
    def write_items(self) -> None:
        rom = self.rom
        # Handle minor locations
        minor_locs = self.settings.minor_locs
        MINOR_LOCS_ARRAY = rom.read_ptr(MINOR_LOCS_ARRAY_ADDR)
        prev_area_room = (-1, -1)
        room_tank_count = 0
        total_metroids = 0
        for min_loc in minor_locs:
            if min_loc.new_item == ItemType.INFANT_METROID:
                total_metroids += 1

            # Update room tank count
            area_room = (min_loc.area, min_loc.room)
            if area_room == prev_area_room:
                room_tank_count += 1
            else:
                room_tank_count = 1
                prev_area_room = area_room
            tank_slot = room_tank_count - 1

            # Overwrite clipdata
            room = RoomEntry(rom, min_loc.area, min_loc.room)
            val = HIDDEN_TANK_CLIP[tank_slot] if min_loc.hidden else TANK_CLIP[tank_slot]
            with room.load_clip() as clip:
                clip.set_block_value(min_loc.block_x, min_loc.block_y, val)
            # Overwrite BG1 if not hidden
            if not min_loc.hidden:
                # Get tilemap
                tileset = Tileset(rom, room.tileset())
                addr = tileset.rle_tilemap_addr()
                # Find tank in tilemap
                addr += 2 + (TANK_BG1_START * 8)
                tile = TANK_TILE[tank_slot]
                idx = next(i for i in range(16) if rom.read_8(addr + i * 8) == tile)
                val = TANK_BG1_START + idx
                with room.load_bg1() as bg1:
                    bg1.set_block_value(min_loc.block_x, min_loc.block_y, val)

            # Write to minors array
            # Assembly has:
            # - A list that contains pointers to below area array
            # - An array with 16 elements per each area, that contains
            #   sorted internal room ids which, contain minor items
            # - An array right after that contains the index where this room starts in
            #   the big item array
            # - A big array of all items and their attributes.
            area_addr = MINOR_LOCS_TABLE_ADDR + (min_loc.area * 4)
            rooms_list_addr = rom.read_ptr(area_addr)
            room_entry_addr = self._binary_search_rooms_array(rooms_list_addr, min_loc.room)
            assert room_entry_addr != -1
            room_entry_index = rom.read_8(room_entry_addr + 16)

            found_item = False
            item_index = -1
            item_addr = -1
            while not found_item:
                item_index += 1
                item_addr = MINOR_LOCS_ARRAY + ((room_entry_index + item_index) * MINOR_LOC_SIZE)
                read_area = rom.read_8(item_addr)
                read_room = rom.read_8(item_addr + 1)
                _read_room_index = rom.read_8(item_addr + 2)
                read_block_x = rom.read_8(item_addr + 3)
                read_block_y = rom.read_8(item_addr + 4)

                assert read_area == min_loc.area, (
                    f"area was '{read_area}', but was expected to be {min_loc.area}"
                )
                assert read_room == min_loc.room, (
                    f"room was '{read_room}', but was expected to be {min_loc.room}"
                )
                found_item = (read_block_x == min_loc.block_x) and (read_block_y == min_loc.block_y)

            assert item_addr != -1

            if min_loc.new_item != ItemType.UNDEFINED:
                rom.write_8(item_addr + 5, min_loc.new_item.value)
                if min_loc.item_sprite != ItemSprite.UNCHANGED:
                    rom.write_8(item_addr + 6, min_loc.item_sprite.value)

        # Handle major locations
        for maj_loc in self.settings.major_locs:
            # Write to majors table
            if maj_loc.new_item != ItemType.UNDEFINED:
                if maj_loc.new_item == ItemType.INFANT_METROID:
                    total_metroids += 1
                addr = MAJOR_LOCS_ADDR + (maj_loc.major_src.value * MAJOR_LOC_SIZE)
                rom.write_8(addr, maj_loc.new_item.value)

        # Write total metroid count
        rom.write_8(TOTAL_METROID_COUNT_ADDR, total_metroids)


# TODO: Move these?
def set_required_metroid_count(rom: Rom, count: int) -> None:
    rom.write_8(REQUIRED_METROID_COUNT_ADDR, count)


def set_tank_increments(rom: Rom, data: MarsschemaTankincrements) -> None:
    rom.write_16(TANK_INC_ADDR, data["MissileTank"])
    rom.write_16(TANK_INC_ADDR + 2, data["EnergyTank"])
    rom.write_16(TANK_INC_ADDR + 4, data["PowerBombTank"])
