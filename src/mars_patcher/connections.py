from typing import Dict, List, Sequence, Tuple

import mars_patcher.constants.game_data as gd
from mars_patcher.constants.main_hub_numbers import (
    MAIN_HUB_CENTER_ROOM,
    MAIN_HUB_CENTER_SMALL_NUM_COORDS_1,
    MAIN_HUB_CENTER_SMALL_NUM_COORDS_2,
    MAIN_HUB_ELE_DOORS,
    MAIN_HUB_ELE_ROOM_LARGE_NUM_COORD,
    MAIN_HUB_ELE_ROOM_SMALL_NUM_COORDS,
    MAIN_HUB_ELE_ROOMS,
    MAIN_HUB_GFX_ADDR,
    MAIN_HUB_LARGE_NUM_BLOCKS,
    MAIN_HUB_SMALL_NUM_BLOCK,
    MAIN_HUB_TILEMAP_ADDR,
)
from mars_patcher.data import get_data_path
from mars_patcher.rom import Rom
from mars_patcher.room_entry import RoomEntry

# Area ID, Room ID, Is area connection
ELEVATOR_TOPS = {
    "OperationsDeckTop": (0, 0x1A, False),
    "MainHubToSector1": (0, 0x43, True),
    "MainHubToSector2": (0, 0x44, True),
    "MainHubToSector3": (0, 0x45, True),
    "MainHubToSector4": (0, 0x46, True),
    "MainHubToSector5": (0, 0x47, True),
    "MainHubToSector6": (0, 0x48, True),
    "MainHubTop": (0, 0x5E, False),
    "HabitationDeckTop": (0, 0xB2, False),
    "Sector1ToRestrictedLab": (1, 0x41, True)
}

ELEVATOR_BOTTOMS = {
    "OperationsDeckBottom": (0, 0x19, False),
    "MainHubBottom": (0, 0x32, False),
    "RestrictedLabToSector1": (0, 0x9A, True),
    "HabitationDeckBottom": (0, 0xB1, False),
    "Sector1ToMainHub": (1, 0x00, True),
    "Sector2ToMainHub": (2, 0x00, True),
    "Sector3ToMainHub": (3, 0x00, True),
    "Sector4ToMainHub": (4, 0x00, True),
    "Sector5ToMainHub": (5, 0x00, True),
    "Sector6ToMainHub": (6, 0x00, True)
}

DOOR_TYPE_AREA_CONN = 1
DOOR_TYPE_NO_HATCH = 2


class Connections:
    """Class for handling elevator shuffle and sector shortcut shuffle."""

    def __init__(self, rom: Rom):
        self.rom = rom
        self.area_doors_ptrs = gd.area_doors_ptrs(rom)
        self.area_conns_addr = gd.area_connections(rom)
        self.area_conns_count = gd.area_connections_count(rom)

    def set_elevator_connections(self, data: Dict) -> None:
        # repoint area connections data
        size = self.area_conns_count * 3
        # reserve space for 8 more area connections
        new_size = size + 8 * 3
        ac_addr = self.rom.reserve_free_space(new_size)
        self.rom.copy_bytes(self.area_conns_addr, ac_addr, size)
        self.rom.write_ptr(0x6945C, ac_addr)
        self.area_conns_addr = ac_addr

        # connect tops to bottoms
        pairs = data["ElevatorTops"]
        self.connect_elevators(ELEVATOR_TOPS, ELEVATOR_BOTTOMS, pairs)
        # connect bottoms to tops
        pairs = data["ElevatorBottoms"]
        self.connect_elevators(ELEVATOR_BOTTOMS, ELEVATOR_TOPS, pairs)
        # update area number tiles in main hub rooms
        self.fix_main_hub_tiles()

    def connect_elevators(
        self, src_dict: Dict, dst_dict: Dict, pairs: Dict[str, str]
    ) -> None:
        for src_name, dst_name in pairs.items():
            src_area, src_door, in_list = src_dict[src_name]
            dst_area, dst_door, _ = dst_dict[dst_name]
            # modify door entry
            self.connect_doors(src_area, src_door, dst_area, dst_door, True)
            # modify area connection
            self.connect_areas(src_area, src_door, dst_area, in_list)

    def connect_doors(
        self, src_area: int, src_door: int, dst_area: int, dst_door: int, is_elevator: bool
    ) -> None:
        addr = self.rom.read_ptr(self.area_doors_ptrs + src_area * 4) + src_door * 0xC
        if is_elevator:
            # fix door type
            props = self.rom.read_8(addr)
            door_type = DOOR_TYPE_AREA_CONN if src_area != dst_area else DOOR_TYPE_NO_HATCH
            self.rom.write_8(addr, props & 0xF0 | door_type)
        # set destination door
        self.rom.write_8(addr + 6, dst_door)

    def connect_areas(self, src_area: int, src_door: int, dst_area: int, in_list: bool) -> None:
        rom = self.rom
        same_area = src_area == dst_area
        if in_list:
            # find existing area connection
            for i in range(self.area_conns_count):
                addr = self.area_conns_addr + i * 3
                if rom.read_8(addr) == src_area and rom.read_8(addr + 1) == src_door:
                    if same_area:
                        # make entry blank
                        rom.write_8(addr, 0)
                        rom.write_8(addr + 1, 0)
                        rom.write_8(addr + 2, 0)
                    else:
                        rom.write_8(addr + 2, dst_area)
                    return
            raise ValueError(f"Area connection not found for Area {src_area} Door {src_door:02X}")
        elif not same_area:
            addr = self.area_conns_addr + self.area_conns_count * 3
            rom.write_8(addr, src_area)
            rom.write_8(addr + 1, src_door)
            rom.write_8(addr + 2, dst_area)
            self.area_conns_count += 1

    def fix_main_hub_tiles(self) -> None:
        # get areas that the 6 elevators go to
        ele_areas = [0 for _ in MAIN_HUB_ELE_DOORS]
        for i in range(self.area_conns_count):
            addr = self.area_conns_addr + i * 3
            # skip if not main deck
            if self.rom.read_8(addr) != 0:
                continue
            door = self.rom.read_8(addr + 1)
            for j, ele_door in enumerate(MAIN_HUB_ELE_DOORS):
                if door == ele_door:
                    ele_areas[j] = self.rom.read_8(addr + 2)
                    break

        # write new graphics and tilemap
        path = get_data_path("main_hub.gfx.lz")
        with open(path, "rb") as f:
            gfx = f.read()
        self.rom.write_bytes(MAIN_HUB_GFX_ADDR, gfx)
        path = get_data_path("main_hub_tilemap.bin")
        with open(path, "rb") as f:
            tilemap = f.read()
        self.rom.write_bytes(MAIN_HUB_TILEMAP_ADDR + 2, tilemap)

        # overwrite numbers on BG2
        # central room
        room_entry = RoomEntry(self.rom, 0, MAIN_HUB_CENTER_ROOM)
        room_entry.load_bg2()
        self.write_main_hub_small_nums(room_entry, MAIN_HUB_CENTER_SMALL_NUM_COORDS_1, ele_areas)
        self.write_main_hub_small_nums(room_entry, MAIN_HUB_CENTER_SMALL_NUM_COORDS_2, ele_areas)
        room_entry.write_bg2()
        # elevator rooms
        large_x, large_y = MAIN_HUB_ELE_ROOM_LARGE_NUM_COORD
        for i, room in enumerate(MAIN_HUB_ELE_ROOMS):
            coords = MAIN_HUB_ELE_ROOM_SMALL_NUM_COORDS[i]
            room_entry = RoomEntry(self.rom, 0, room)
            room_entry.load_bg2()
            self.write_main_hub_small_nums(room_entry, coords, ele_areas)
            block = MAIN_HUB_LARGE_NUM_BLOCKS[ele_areas[i]]
            room_entry.set_bg2_block(block, large_x, large_y)
            room_entry.set_bg2_block(block + 0x10, large_x, large_y + 1)
            room_entry.write_bg2()

    def write_main_hub_small_nums(
        self,
        room_entry: RoomEntry,
        coords: Sequence[Tuple[int, int] | None],
        ele_areas: List[int]
    ) -> None:
        for area, coord in enumerate(coords):
            if coord is None:
                continue
            block = MAIN_HUB_SMALL_NUM_BLOCK + ele_areas[area] * 0x10
            if area % 2 == 0:
                block += 2
            x, y = coord
            room_entry.set_bg2_block(block, x, y)
            room_entry.set_bg2_block(block + 1, x + 1, y)
