import random
from typing import Dict, List

from mars_patcher.rom import Rom
import mars_patcher.constants.game_data as gd


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

AREA_CONNECTIONS_ADDR = 0x7FF300

DOOR_TYPE_AREA_CONN = 1
DOOR_TYPE_NO_HATCH = 2


class Connections:
    def __init__(self, rom: Rom):
        self.rom = rom
        self.area_doors_ptrs = gd.area_doors_ptrs(rom)
        self.area_conns_addr = gd.area_connections(rom)
        self.area_conns_count = gd.area_connections_count(rom)
    
    def set_elevator_connections(self, data: Dict) -> None:
        # repoint area connections data
        # TODO: move to asm
        ac_addr = AREA_CONNECTIONS_ADDR
        self.rom.copy_bytes(self.area_conns_addr, ac_addr, self.area_conns_count * 3)
        self.rom.write_ptr(0x6945C, ac_addr)
        self.area_conns_addr = ac_addr
        
        # connect tops to bottoms
        pairs = data["ElevatorTops"]
        self.connect_elevators(ELEVATOR_TOPS, ELEVATOR_BOTTOMS, pairs)
        # connect bottoms to tops
        pairs = data["ElevatorBottoms"]
        self.connect_elevators(ELEVATOR_BOTTOMS, ELEVATOR_TOPS, pairs)

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

    def print_area_conns(self) -> None:
        addr = self.area_conns_addr
        for _ in range(self.area_conns_count):
            src_area = self.rom.read_8(addr)
            src_door = self.rom.read_8(addr + 1)
            dst_area = self.rom.read_8(addr + 2)
            print(f"Area {src_area} Door {src_door:02X} -> Area {dst_area}")
            addr += 3
