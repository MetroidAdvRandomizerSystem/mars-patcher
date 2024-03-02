import json
from enum import Enum
from typing import Any, Dict, List

from mars_patcher.data import get_data_path


class MajorSource(Enum):
    MAIN_DECK_DATA = 0
    ARACHNUS = 1
    CHARGE_CORE_X = 2
    LEVEL_1 = 3
    TRO_DATA = 4
    ZAZABI = 5
    SERRIS = 6
    LEVEL_2 = 7
    PYR_DATA = 8
    MEGA_X = 9
    LEVEL_3 = 10
    ARC_DATA_1 = 11
    WIDE_CORE_X = 12
    ARC_DATA_2 = 13
    YAKUZA = 14
    NETTORI = 15
    NIGHTMARE = 16
    LEVEL_4 = 17
    AQA_DATA = 18
    WAVE_CORE_X = 19
    RIDLEY = 20


class ItemType(Enum):
    UNDEFINED = -1
    NONE = 0
    MISSILES = 1
    MORPH_BALL = 2
    CHARGE_BEAM = 3
    LEVEL_1 = 4
    BOMBS = 5
    HI_JUMP = 6
    SPEED_BOOSTER = 7
    LEVEL_2 = 8
    SUPER_MISSILES = 9
    VARIA_SUIT = 10
    LEVEL_3 = 11
    ICE_MISSILES = 12
    WIDE_BEAM = 13
    POWER_BOMBS = 14
    SPACE_JUMP = 15
    PLASMA_BEAM = 16
    GRAVITY_SUIT = 17
    LEVEL_4 = 18
    DIFFUSION_MISSILES = 19
    WAVE_BEAM = 20
    SCREW_ATTACK = 21
    ICE_BEAM = 22
    MISSILE_TANK = 23
    ENERGY_TANK = 24
    POWER_BOMB_TANK = 25

    def __le__(self, other: Any) -> bool:
        if isinstance(other, ItemType):
            return self.value <= other.value
        return NotImplemented


class ItemSprite(Enum):
    UNCHANGED = -1
    EMPTY = 0
    MISSILES = 1
    MORPH_BALL = 2
    CHARGE_BEAM = 3
    LEVEL_1 = 4
    BOMBS = 5
    HI_JUMP = 6
    SPEED_BOOSTER = 7
    LEVEL_2 = 8
    SUPER_MISSILES = 9
    VARIA_SUIT = 10
    LEVEL_3 = 11
    ICE_MISSILES = 12
    WIDE_BEAM = 13
    POWER_BOMBS = 14
    SPACE_JUMP = 15
    PLASMA_BEAM = 16
    GRAVITY_SUIT = 17
    LEVEL_4 = 18
    DIFFUSION_MISSILES = 19
    WAVE_BEAM = 20
    SCREW_ATTACK = 21
    ICE_BEAM = 22
    MISSILE_TANK = 23
    ENERGY_TANK = 24
    POWER_BOMB_TANK = 25
    ANONYMOUS = 26
    SHINY_MISSILE_TANK = 27
    SHINY_POWER_BOMB_TANK = 28


class Location:
    def __init__(
        self, area: int, room: int, orig_item: ItemType, new_item: ItemType = ItemType.UNDEFINED
    ):
        if type(self) is Location:
            raise TypeError()
        self.area = area
        self.room = room
        self.orig_item = orig_item
        self.new_item = new_item

    def __str__(self) -> str:
        item_str = self.orig_item.name
        if self.new_item != ItemType.UNDEFINED:
            item_str += "/" + self.new_item.name
        return f"{self.area},{self.room:02X}: {item_str}"


class MajorLocation(Location):
    def __init__(
        self,
        area: int,
        room: int,
        major_src: MajorSource,
        orig_item: ItemType,
        new_item: ItemType = ItemType.UNDEFINED,
    ):
        super().__init__(area, room, orig_item, new_item)
        self.major_src = major_src


class MinorLocation(Location):
    def __init__(
        self,
        area: int,
        room: int,
        block_x: int,
        block_y: int,
        hidden: bool,
        orig_item: ItemType,
        new_item: ItemType = ItemType.UNDEFINED,
        item_sprite: ItemSprite = ItemSprite.UNCHANGED
    ):
        super().__init__(area, room, orig_item, new_item)
        self.block_x = block_x
        self.block_y = block_y
        self.hidden = hidden
        self.item_sprite = item_sprite


KEY_MAJOR_LOCS = "MajorLocations"
KEY_MINOR_LOCS = "MinorLocations"
KEY_AREA = "Area"
KEY_ROOM = "Room"
KEY_SOURCE = "Source"
KEY_BLOCK_X = "BlockX"
KEY_BLOCK_Y = "BlockY"
KEY_HIDDEN = "Hidden"
KEY_ORIGINAL = "Original"
KEY_ITEM = "Item"
KEY_ITEM_SPRITE = "ItemSprite"


class LocationSettings:
    SOURCE_ENUMS = {
        "MainDeckData": MajorSource.MAIN_DECK_DATA,
        "Arachnus": MajorSource.ARACHNUS,
        "ChargeCoreX": MajorSource.CHARGE_CORE_X,
        "Level1": MajorSource.LEVEL_1,
        "TroData": MajorSource.TRO_DATA,
        "Zazabi": MajorSource.ZAZABI,
        "Serris": MajorSource.SERRIS,
        "Level2": MajorSource.LEVEL_2,
        "PyrData": MajorSource.PYR_DATA,
        "MegaX": MajorSource.MEGA_X,
        "Level3": MajorSource.LEVEL_3,
        "ArcData1": MajorSource.ARC_DATA_1,
        "WideCoreX": MajorSource.WIDE_CORE_X,
        "ArcData2": MajorSource.ARC_DATA_2,
        "Yakuza": MajorSource.YAKUZA,
        "Nettori": MajorSource.NETTORI,
        "Nightmare": MajorSource.NIGHTMARE,
        "Level4": MajorSource.LEVEL_4,
        "AqaData": MajorSource.AQA_DATA,
        "WaveCoreX": MajorSource.WAVE_CORE_X,
        "Ridley": MajorSource.RIDLEY,
    }

    ITEM_ENUMS = {
        "Undefined": ItemType.UNDEFINED,
        "None": ItemType.NONE,
        "Missiles": ItemType.MISSILES,
        "MorphBall": ItemType.MORPH_BALL,
        "ChargeBeam": ItemType.CHARGE_BEAM,
        "Level1": ItemType.LEVEL_1,
        "Bombs": ItemType.BOMBS,
        "HiJump": ItemType.HI_JUMP,
        "SpeedBooster": ItemType.SPEED_BOOSTER,
        "Level2": ItemType.LEVEL_2,
        "SuperMissiles": ItemType.SUPER_MISSILES,
        "VariaSuit": ItemType.VARIA_SUIT,
        "Level3": ItemType.LEVEL_3,
        "IceMissiles": ItemType.ICE_MISSILES,
        "WideBeam": ItemType.WIDE_BEAM,
        "PowerBombs": ItemType.POWER_BOMBS,
        "SpaceJump": ItemType.SPACE_JUMP,
        "PlasmaBeam": ItemType.PLASMA_BEAM,
        "GravitySuit": ItemType.GRAVITY_SUIT,
        "Level4": ItemType.LEVEL_4,
        "DiffusionMissiles": ItemType.DIFFUSION_MISSILES,
        "WaveBeam": ItemType.WAVE_BEAM,
        "ScrewAttack": ItemType.SCREW_ATTACK,
        "IceBeam": ItemType.ICE_BEAM,
        "MissileTank": ItemType.MISSILE_TANK,
        "EnergyTank": ItemType.ENERGY_TANK,
        "PowerBombTank": ItemType.POWER_BOMB_TANK,
    }

    ITEM_SPRITE_ENUMS = {
        "Empty": ItemSprite.EMPTY,
        "Missiles": ItemSprite.MISSILES,
        "MorphBall": ItemSprite.MORPH_BALL,
        "ChargeBeam": ItemSprite.CHARGE_BEAM,
        "Level1": ItemSprite.LEVEL_1,
        "Bombs": ItemSprite.BOMBS,
        "HiJump": ItemSprite.HI_JUMP,
        "SpeedBooster": ItemSprite.SPEED_BOOSTER,
        "Level2": ItemSprite.LEVEL_2,
        "SuperMissiles": ItemSprite.SUPER_MISSILES,
        "VariaSuit": ItemSprite.VARIA_SUIT,
        "Level3": ItemSprite.LEVEL_3,
        "IceMissiles": ItemSprite.ICE_MISSILES,
        "WideBeam": ItemSprite.WIDE_BEAM,
        "PowerBombs": ItemSprite.POWER_BOMBS,
        "SpaceJump": ItemSprite.SPACE_JUMP,
        "PlasmaBeam": ItemSprite.PLASMA_BEAM,
        "GravitySuit": ItemSprite.GRAVITY_SUIT,
        "Level4": ItemSprite.LEVEL_4,
        "DiffusionMissiles": ItemSprite.DIFFUSION_MISSILES,
        "WaveBeam": ItemSprite.WAVE_BEAM,
        "ScrewAttack": ItemSprite.SCREW_ATTACK,
        "IceBeam": ItemSprite.ICE_BEAM,
        "MissileTank": ItemSprite.MISSILE_TANK,
        "EnergyTank": ItemSprite.ENERGY_TANK,
        "PowerBombTank": ItemSprite.POWER_BOMB_TANK,
        "Anonymous": ItemSprite.ANONYMOUS,
        "ShinyMissileTank": ItemSprite.SHINY_MISSILE_TANK,
        "ShinyPowerBombTank": ItemSprite.SHINY_POWER_BOMB_TANK
    }

    def __init__(self, major_locs: List[MajorLocation], minor_locs: List[MinorLocation]):
        self.major_locs = major_locs
        self.minor_locs = minor_locs

    @classmethod
    def load(cls) -> "LocationSettings":
        with open(get_data_path("locations.json")) as f:
            data = json.load(f)

        major_locs = []
        for entry in data[KEY_MAJOR_LOCS]:
            major_loc = MajorLocation(
                entry[KEY_AREA],
                entry[KEY_ROOM],
                cls.SOURCE_ENUMS[entry[KEY_SOURCE]],
                cls.ITEM_ENUMS[entry[KEY_ORIGINAL]],
            )
            major_locs.append(major_loc)

        minor_locs = []
        for entry in data[KEY_MINOR_LOCS]:
            minor_loc = MinorLocation(
                entry[KEY_AREA],
                entry[KEY_ROOM],
                entry[KEY_BLOCK_X],
                entry[KEY_BLOCK_Y],
                entry[KEY_HIDDEN],
                cls.ITEM_ENUMS[entry[KEY_ORIGINAL]],
            )
            minor_locs.append(minor_loc)

        return LocationSettings(major_locs, minor_locs)

    def set_assignments(self, data: Dict) -> None:
        for maj_loc_entry in data[KEY_MAJOR_LOCS]:
            # get source and item
            source = self.SOURCE_ENUMS[maj_loc_entry[KEY_SOURCE]]
            item = self.ITEM_ENUMS[maj_loc_entry[KEY_ITEM]]
            # find location with this source
            maj_loc = next(m for m in self.major_locs if m.major_src == source)
            maj_loc.new_item = item

        for min_loc_entry in data[KEY_MINOR_LOCS]:
            # get area, room, block X, block Y
            area = min_loc_entry[KEY_AREA]
            room = min_loc_entry[KEY_ROOM]
            block_x = min_loc_entry[KEY_BLOCK_X]
            block_y = min_loc_entry[KEY_BLOCK_Y]
            # find location with this source
            try:
                min_loc = next(
                    m
                    for m in self.minor_locs
                    if m.area == area
                    and m.room == room
                    and m.block_x == block_x
                    and m.block_y == block_y
                )
            except StopIteration:
                raise ValueError(
                    f"Invalid minor location: Area {area}, Room {room}, X {block_x}, Y {block_y}"
                )
            # set item and item sprite
            item = self.ITEM_ENUMS[min_loc_entry[KEY_ITEM]]
            min_loc.new_item = item
            if KEY_ITEM_SPRITE in min_loc_entry:
                min_loc.item_sprite = self.ITEM_SPRITE_ENUMS[min_loc_entry[KEY_ITEM_SPRITE]]
