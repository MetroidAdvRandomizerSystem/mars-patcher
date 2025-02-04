from mars_patcher.auto_generated_types import Areaid, MarsschemaRoomnamesItem, Typeu8
from mars_patcher.constants.reserved_space import ReservedConstants
from mars_patcher.rom import Rom
from mars_patcher.text import MessageType, encode_text

ROOM_NAMES_TABLE_ADDR = ReservedConstants.ROOM_NAMES_TABLE_ADDR


# Write Room Names to ROM
# Assembly has:
# - A list that contains pointers to area room names
# - Area Room names are indexed by room id. This means some entries
#   are never used, but this allows for easy lookup
def write_room_names(rom: Rom, data: list[MarsschemaRoomnamesItem]) -> None:
    seen_rooms: set[tuple[Areaid, Typeu8]] = set()
    for room_name_entry in data:
        area_id = room_name_entry["Area"]
        room_id = room_name_entry["Room"]
        room_name = room_name_entry["Name"]

        # Check that the room wasn't already set
        assert (area_id, room_id) not in seen_rooms, "Duplicate room name provided."
        seen_rooms.add((area_id, room_id))

        # Find room name table by indexing at ROOM_NAMES_TABLE_ADDR
        area_addr = ROOM_NAMES_TABLE_ADDR + (area_id * 4)
        area_room_name_addr = rom.read_ptr(area_addr)

        # Find specific room by indexing by the room_id
        room_name_addr = area_room_name_addr + (room_id * 4)

        encoded_text = encode_text(rom, MessageType.TWO_LINE, room_name)
        message_addr = rom.reserve_free_space(len(encoded_text) * 2)
        rom.write_ptr(room_name_addr, message_addr)
        rom.write_16_list(message_addr, encoded_text)
