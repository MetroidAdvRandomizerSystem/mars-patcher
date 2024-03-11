from mars_patcher.patching import IpsDecoder
from mars_patcher.data import get_data_path
from mars_patcher.rom import Rom


def get_patch_path(rom: Rom, filename: str) -> str:
    dir = f"{rom.game.name}_{rom.region.name}".lower()
    return get_data_path("patches", dir, filename)


def skip_door_transitions(rom: Rom) -> None:
    # TODO: move to patch
    rom.write_32(0x69500, 0x3000BDE)
    rom.write_8(0x694E2, 0xC)


def stereo_default(rom: Rom) -> None:
    path = get_patch_path(rom, "stereo_default.ips")
    with open(path, "rb") as f:
        patch = f.read()
    IpsDecoder().apply_patch(patch, rom.data)
