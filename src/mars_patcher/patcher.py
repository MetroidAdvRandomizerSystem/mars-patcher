import json
from typing import Callable

from jsonschema import validate

from mars_patcher.connections import Connections
from mars_patcher.credits import write_credits
from mars_patcher.data import get_data_path
from mars_patcher.door_locks import remove_door_colors_on_minimap, set_door_locks
from mars_patcher.item_patcher import ItemPatcher, set_required_metroid_count, set_tank_increments
from mars_patcher.level_edits import apply_level_edits
from mars_patcher.locations import LocationSettings
from mars_patcher.minimap import apply_minimap_edits
from mars_patcher.misc_patches import (
    apply_anti_softlock_edits,
    apply_pbs_without_bombs,
    apply_unexplored_map,
    change_missile_limit,
    disable_demos,
    disable_music,
    disable_sound_effects,
    skip_door_transitions,
    stereo_default,
)
from mars_patcher.navigation_text import NavigationText
from mars_patcher.random_palettes import PaletteRandomizer, PaletteSettings
from mars_patcher.rom import Rom
from mars_patcher.starting import set_starting_items, set_starting_location
from mars_patcher.text import write_seed_hash


def validate_patch_data(patch_data: dict) -> None:
    """
    Validates whether the specified patch_data satisifies the schema for it.

    Raises:
        ValidationError: If the patch data does not satisfy the schema.
    """
    with open(get_data_path("schema.json")) as f:
        schema = json.load(f)
    validate(patch_data, schema)


def patch(
    input_path: str,
    output_path: str,
    patch_data: dict,
    status_update: Callable[[str, float], None],
) -> None:
    # Load input rom
    rom = Rom(input_path)

    if patch_data.get("AntiSoftlockRoomEdits"):
        apply_anti_softlock_edits(rom)

    # Randomize palettes - palettes are randomized first in case the item
    # patcher needs to copy tilesets
    if "Palettes" in patch_data:
        status_update(-1, "Randomizing palettes...")
        pal_settings = PaletteSettings.from_json(patch_data["Palettes"])
        pal_randomizer = PaletteRandomizer(rom, pal_settings)
        pal_randomizer.randomize()

    # Load locations and set assignments
    status_update(-1, "Writing item assignments...")
    loc_settings = LocationSettings.initialize()
    loc_settings.set_assignments(patch_data["Locations"])
    item_patcher = ItemPatcher(rom, loc_settings)
    item_patcher.write_items()

    # Required metroid count
    set_required_metroid_count(rom, patch_data["RequiredMetroidCount"])

    # Starting location
    if "StartingLocation" in patch_data:
        status_update(-1, "Writing starting location...")
        set_starting_location(rom, patch_data["StartingLocation"])

    # Starting items
    if "StartingItems" in patch_data:
        status_update(-1, "Writing starting items...")
        set_starting_items(rom, patch_data["StartingItems"])

    # Tank increments
    if "TankIncrements" in patch_data:
        status_update(-1, "Writing tank increments...")
        set_tank_increments(rom, patch_data["TankIncrements"])

    # Elevator connections
    conns = None
    if "ElevatorConnections" in patch_data:
        status_update(-1, "Writing elevator connections...")
        conns = Connections(rom)
        conns.set_elevator_connections(patch_data["ElevatorConnections"])

    # Sector shortcuts
    if "SectorShortcuts" in patch_data:
        status_update(-1, "Writing sector shortcuts...")
        if conns is None:
            conns = Connections(rom)
        conns.set_shortcut_connections(patch_data["SectorShortcuts"])

    # Door locks
    if "DoorLocks" in patch_data:
        status_update(-1, "Writing door locks...")
        set_door_locks(rom, patch_data["DoorLocks"])

    # Hints
    if "NavigationText" in patch_data:
        status_update(-1, "Writing navigation text...")
        navigation_text = NavigationText.from_json(patch_data["NavigationText"])
        navigation_text.write(rom)

    # Credits
    if "CreditsText" in patch_data:
        status_update(-1, "Writing credits text...")
        write_credits(rom, patch_data["CreditsText"])

    # Misc patches

    if patch_data.get("DisableDemos"):
        disable_demos(rom)

    if patch_data.get("SkipDoorTransitions"):
        skip_door_transitions(rom)

    if patch_data.get("StereoDefault", True):
        stereo_default(rom)

    if patch_data.get("DisableMusic"):
        disable_music(rom)

    if patch_data.get("DisableSoundEffects"):
        disable_sound_effects(rom)

    if "MissileLimit" in patch_data:
        change_missile_limit(rom, patch_data["MissileLimit"])

    if patch_data.get("PowerBombsWithoutBombs"):
        apply_pbs_without_bombs(rom)

    if patch_data.get("UnexploredMap"):
        apply_unexplored_map(rom)

    if patch_data.get("DoorLocks") or "HideDoorsOnMinimap" in patch_data:
        remove_door_colors_on_minimap(rom)

    if "LevelEdits" in patch_data:
        apply_level_edits(rom, patch_data["LevelEdits"])

    if "MinimapEdits" in patch_data:
        apply_minimap_edits(rom, patch_data["MinimapEdits"])

    write_seed_hash(rom, patch_data["SeedHash"])

    rom.save(output_path)
    status_update(-1, f"Output written to {output_path}")

    # Remove once in public beta
    print("------")
    print("Report all issues to the Randovania Discord Server (https://discord.gg/M23gCxj6fw)")
    print(
        "or alternatively this project's issue page (https://github.com/MetroidAdvRandomizerSystem/mars-patcher/issues)"
    )
    print("Thank you")
