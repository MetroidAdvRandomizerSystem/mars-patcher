import json
from typing import Callable

from jsonschema import validate

from mars_patcher.data import get_data_path
from mars_patcher.item_patcher import ItemPatcher, set_metroid_count, set_tank_increments
from mars_patcher.locations import LocationSettings
from mars_patcher.misc_patches import *
from mars_patcher.navigation_text import NavigationText
from mars_patcher.random_palettes import PaletteRandomizer, PaletteSettings
from mars_patcher.rom import Rom
from mars_patcher.starting import set_starting_items, set_starting_location
from mars_patcher.text import write_seed_hash


def patch(input_path: str,
          output_path: str,
          patch_data_path: str,
          status_update: Callable[[float, str], None]
          ) -> None:
    # load input rom
    rom = Rom(input_path)

    # load patch data file and validate
    with open(patch_data_path) as f:
        patch_data = json.load(f)

    with open(get_data_path("schema.json")) as f:
        schema = json.load(f)
    validate(patch_data, schema)

    # randomize palettes - palettes are randomized first in case the item
    # patcher needs to copy tilesets
    if "Palettes" in patch_data:
        status_update(-1, "Randomizing palettes...")
        pal_settings = PaletteSettings.from_json(patch_data["Palettes"])
        pal_randomizer = PaletteRandomizer(rom, pal_settings)
        pal_randomizer.randomize()

    # load locations and set assignments
    status_update(-1, "Writing item assignments...")
    loc_settings = LocationSettings.initialize()
    loc_settings.set_assignments(patch_data["Locations"])
    item_patcher = ItemPatcher(rom, loc_settings)
    item_patcher.write_items()

    # required metroid count
    set_metroid_count(rom, patch_data["RequiredMetroidCount"])

    # starting location
    if "StartingLocation" in patch_data:
        status_update(-1, "Writing starting location...")
        set_starting_location(rom, patch_data["StartingLocation"])

    # starting items
    if "StartingItems" in patch_data:
        status_update(-1, "Writing starting items...")
        set_starting_items(rom, patch_data["StartingItems"])

    # tank increments
    if "TankIncrements" in patch_data:
        status_update(-1, "Writing tank increments...")
        set_tank_increments(rom, patch_data["TankIncrements"])

    # hints
    if "NavigationText" in patch_data:
        status_update(-1, "Writing navigation text...")
        navigation_text = NavigationText.from_json(patch_data["NavigationText"])
        navigation_text.write(rom)

    if patch_data.get("SkipDoorTransitions"):
        skip_door_transitions(rom)
    
    if patch_data.get("StereoDefault", True):
        stereo_default(rom)
    
    if patch_data.get("DisableMusic"):
        disable_music(rom)

    if patch_data.get("DisableSoundEffects"):
        disable_sound_effects(rom)

    write_seed_hash(rom, patch_data["SeedHash"])

    rom.save(output_path)
    status_update(-1, f"Output written to {output_path}")
