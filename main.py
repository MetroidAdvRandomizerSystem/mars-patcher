import argparse

from item_patcher import ItemPatcher
from locations import load_locations, set_assignments
from random_palettes import PaletteRandomizer
from rom import Rom
from settings import Settings, HueFormat


if __name__ == "__main__":
    FORMAT_HSV = "hsv"
    FORMAT_LAB = "lab"

    parser = argparse.ArgumentParser()
    # GBA ROM input/output paths
    parser.add_argument("rom_path", type=str,
        help="Path to a GBA ROM file")
    parser.add_argument("out_path", type=str,
        help="Path to output ROM file")
    # random items
    parser.add_argument("-il", "--item_list_path", type=str,
        help="Path to item assignments json file")
    # random palettes
    parser.add_argument("-pt", "--pal_tileset", action="store_true",
        help="Randomize tileset palettes")
    parser.add_argument("-pe", "--pal_enemy", action="store_true",
        help="Randomize enemy palettes")
    parser.add_argument("-ps", "--pal_samus", action="store_true",
        help="Randomize Samus palettes")
    parser.add_argument("-pb", "--pal_beam", action="store_true",
        help="Randomize beam palettes")
    parser.add_argument("-phl", "--pal_hue_min", type=int, default=0,
        help="Minimum hue value in degrees (0-180); default is 0")
    parser.add_argument("-phu", "--pal_hue_max", type=int, default=180,
        help="Minimum hue value in degrees (0-180); default is 180")
    parser.add_argument("-pf", "--pal_format", type=str,
        choices=[FORMAT_HSV, FORMAT_LAB], default=FORMAT_LAB,
        help="Color space to use for hue shifting; default is LAB")
    # other settings
    parser.add_argument("-sdt", "--skip_door_transitions", action="store_true",
        help="Makes all door transitions instant")

    args = parser.parse_args()

    # load input rom
    rom = Rom(args.rom_path)

    # validate palette rando settings
    # check hue
    if args.pal_hue_min < 0 or args.pal_hue_max > 180:
        parser.error("hue must be between 0 and 180")
    if args.pal_hue_min > args.pal_hue_max:
        parser.error("hue_min must be smaller than hue_max")
    # get hue shift format
    if args.pal_format == FORMAT_HSV:
        pal_format = HueFormat.HSV
    elif args.pal_format == FORMAT_LAB:
        pal_format = HueFormat.LAB

    settings = Settings(
        args.item_list_path,
        args.pal_tileset, args.pal_enemy, args.pal_samus, args.pal_beam,
        args.pal_hue_min, args.pal_hue_max, pal_format,
        args.skip_door_transitions
    )

    # randomize palettes
    if settings.rand_palettes():
        pal_randomizer = PaletteRandomizer(rom, settings)
        pal_randomizer.randomize()

    # patch items
    if settings.item_list_path is not None:
        item_patcher = ItemPatcher(rom, settings)
        major_locs, minor_locs = load_locations()
        set_assignments(major_locs, minor_locs, args.item_list_path)
        item_patcher.assign_items(minor_locs, major_locs)

    if settings.skip_door_transitions:
        # TODO: move to patch
        rom.write_32(0x69500, 0x300001F)
        rom.write_16(0x694E4, 0xD000)

    rom.save(args.out_path)
