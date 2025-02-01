from mars_patcher.auto_generated_types import MarsschemaRoomnamesItem
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
    for room_name_dict in data:
        area_id = room_name_dict["Area"]
        room_id = room_name_dict["Room"]
        name = room_name_dict["Name"]

        # Find room name table by indexing at ROOM_NAMES_TABLE_ADDR
        area_addr = ROOM_NAMES_TABLE_ADDR + (area_id * 4)
        area_room_name_addr = rom.read_ptr(area_addr)

        # Find specific room by indexing by the room_id
        room_name_addr = area_room_name_addr + (room_id * 4)

        encoded_text = encode_text(
            rom,
            MessageType.SINGLEPANEL,
            name,
            224,
        )
        message_pointer = rom.reserve_free_space(len(encoded_text) * 2)
        rom.write_ptr(room_name_addr, message_pointer)
        for char in encoded_text:
            rom.write_16(message_pointer, char)
            message_pointer += 2
