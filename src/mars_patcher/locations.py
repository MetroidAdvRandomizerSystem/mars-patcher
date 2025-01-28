import json

from mars_patcher.auto_generated_types import MarsschemaLocations
from mars_patcher.constants.items import (
    ITEM_ENUMS,
    ITEM_SPRITE_ENUMS,
    KEY_AREA,
    KEY_BLOCK_X,
    KEY_BLOCK_Y,
    KEY_HIDDEN,
    KEY_ITEM,
    KEY_ITEM_SPRITE,
    KEY_MAJOR_LOCS,
    KEY_MINOR_LOCS,
    KEY_ORIGINAL,
    KEY_ROOM,
    KEY_SOURCE,
    SOURCE_ENUMS,
    ItemSprite,
    ItemType,
    MajorSource,
)
from mars_patcher.data import get_data_path


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
        return f"{self.area},0x{self.room:02X}: {item_str}"


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
        item_sprite: ItemSprite = ItemSprite.UNCHANGED,
    ):
        super().__init__(area, room, orig_item, new_item)
        self.block_x = block_x
        self.block_y = block_y
        self.hidden = hidden
        self.item_sprite = item_sprite


class LocationSettings:
    def __init__(self, major_locs: list[MajorLocation], minor_locs: list[MinorLocation]):
        self.major_locs = major_locs
        self.minor_locs = minor_locs

    @classmethod
    def initialize(cls) -> "LocationSettings":
        with open(get_data_path("locations.json")) as f:
            data = json.load(f)

        major_locs = []
        for entry in data[KEY_MAJOR_LOCS]:
            major_loc = MajorLocation(
                entry[KEY_AREA],
                entry[KEY_ROOM],
                SOURCE_ENUMS[entry[KEY_SOURCE]],
                ITEM_ENUMS[entry[KEY_ORIGINAL]],
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
                ITEM_ENUMS[entry[KEY_ORIGINAL]],
            )
            minor_locs.append(minor_loc)

        return LocationSettings(major_locs, minor_locs)

    def set_assignments(self, data: MarsschemaLocations) -> None:
        for maj_loc_entry in data[KEY_MAJOR_LOCS]:
            # Get source and item
            source = SOURCE_ENUMS[maj_loc_entry[KEY_SOURCE]]
            item = ITEM_ENUMS[maj_loc_entry[KEY_ITEM]]
            # Find location with this source
            maj_loc = next(m for m in self.major_locs if m.major_src == source)
            maj_loc.new_item = item

        for min_loc_entry in data[KEY_MINOR_LOCS]:
            # Get area, room, block X, block Y
            area = min_loc_entry[KEY_AREA]
            room = min_loc_entry[KEY_ROOM]
            block_x = min_loc_entry[KEY_BLOCK_X]
            block_y = min_loc_entry[KEY_BLOCK_Y]
            # Find location with this source
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
            # Set item and item sprite
            item = ITEM_ENUMS[min_loc_entry[KEY_ITEM]]
            min_loc.new_item = item
            if KEY_ITEM_SPRITE in min_loc_entry:
                min_loc.item_sprite = ITEM_SPRITE_ENUMS[min_loc_entry[KEY_ITEM_SPRITE]]
