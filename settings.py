from enum import Enum


class HueFormat(Enum):
    HSV = 1
    LAB = 2


class Settings(object):
    def __init__(self,
        item_list_path: str = None,
        rand_tileset: bool = True,
        rand_enemy: bool = True,
        rand_samus: bool = True,
        rand_beam: bool = True,
        hue_min: int = 0,
        hue_max: int = 180,
        hue_format: HueFormat = HueFormat.LAB,
        skip_door_transitions: bool = False
    ):
        self.item_list_path = item_list_path
        self.rand_tileset = rand_tileset
        self.rand_enemy = rand_enemy
        self.rand_samus = rand_samus
        self.rand_beam = rand_beam        
        self.hue_min = hue_min
        self.hue_max = hue_max
        self.hue_format = hue_format
        self.skip_door_transitions = skip_door_transitions

    def rand_palettes(self) -> bool:
        return self.rand_tileset or self.rand_enemy or self.rand_samus or self.rand_beam
