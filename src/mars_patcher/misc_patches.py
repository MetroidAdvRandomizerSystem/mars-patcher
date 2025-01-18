import mars_patcher.constants.game_data as gd
from mars_patcher.constants.reserved_space import ReservedConstants
from mars_patcher.data import get_data_path
from mars_patcher.patching import IpsDecoder
from mars_patcher.rom import Rom


def get_patch_path(rom: Rom, filename: str) -> str:
    dir = f"{rom.game.name}_{rom.region.name}".lower()
    return get_data_path("patches", dir, filename)


def apply_patch_in_data_path(rom: Rom, patch_name: str) -> None:
    path = get_patch_path(rom, patch_name)
    with open(path, "rb") as f:
        patch = f.read()
    IpsDecoder().apply_patch(patch, rom.data)


def disable_demos(rom: Rom) -> None:
    # TODO: Move to patch
    # b 0x8087460
    rom.write_16(0x87436, 0xE013)


def skip_door_transitions(rom: Rom) -> None:
    # TODO: Move to patch
    rom.write_32(0x69500, 0x3000BDE)
    rom.write_8(0x694E2, 0xC)


def stereo_default(rom: Rom) -> None:
    apply_patch_in_data_path(rom, "stereo_default.ips")


def disable_sounds(rom: Rom, start: int, end: int, exclude: set[int] = set()) -> None:
    sound_data_addr = gd.sound_data_entries(rom)
    for idx in range(start, end):
        if idx not in exclude:
            addr = sound_data_addr + idx * 8
            rom.write_8(rom.read_ptr(addr), 0)


def disable_music(rom: Rom) -> None:
    # Exclude jingles
    exclude = {
        16,  # Major obtained
        17,  # Loading save
        20,  # Minor obtained
        59,  # Event
    }
    disable_sounds(rom, 0, 100, exclude)


def disable_sound_effects(rom: Rom) -> None:
    disable_sounds(rom, 100, gd.sound_count(rom))


def change_missile_limit(rom: Rom, limit: int) -> None:
    rom.write_8(ReservedConstants.MISSILE_LIMIT_ADDR, limit)


def apply_unexplored_map(rom: Rom) -> None:
    apply_patch_in_data_path(rom, "unhidden_map.ips")


def apply_pbs_without_bombs(rom: Rom) -> None:
    apply_patch_in_data_path(rom, "bombless_pbs.ips")


def apply_anti_softlock_edits(rom: Rom) -> None:
    apply_patch_in_data_path(rom, "anti_softlock.ips")


def apply_hint_security(rom: Rom) -> None:
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR + 0x4, 0x2)  # S1 unlocked by l2
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR + 0x6, 0x2)  # S2 unlocked by l2
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR + 0x8, 0x3)  # S3 unlocked by l3
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR + 0x7, 0x3)  # S4 unlocked by l3
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR + 0x5, 0x4)  # S5 unlocked by l4
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR + 0x9, 0x4)  # S6 unlocked by l4
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR+0xA, 0xFF) # auxiliary always unlocked
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR+0xB, 0xFF) # restricted always unlocked
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR+0x1, 0x5) # main deck 1 always locked
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR+0x2, 0x5) # main deck 2 always locked
    rom.write_8(ReservedConstants.HINT_SECURITY_LEVELS_ADDR+0x3, 0x5) # operations deck always locked
