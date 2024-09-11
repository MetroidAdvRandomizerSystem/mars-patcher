from __future__ import annotations

from types import TracebackType

from mars_patcher.compress import comp_lz77, decomp_lz77
from mars_patcher.constants.game_data import minimap_ptrs
from mars_patcher.rom import Rom

MINIMAP_WIDTH = 32


class Minimap:
    """Class for reading/writing minimap data and setting tiles."""

    def __init__(self, rom: Rom, id: int):
        self.rom = rom
        self.pointer = minimap_ptrs(rom) + (id * 4)
        addr = rom.read_ptr(self.pointer)
        self.tile_data, self.comp_len = decomp_lz77(rom.data, addr)

    def __enter__(self) -> Minimap:
        # We don't need to do anything
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.write()

    def get_tile_value(self, x: int, y: int) -> int:
        idx = (y * MINIMAP_WIDTH + x) * 2
        if idx >= len(self.tile_data):
            raise IndexError(f"Tile coordinate ({x}, {y}) is not within minimap")
        return self.tile_data[idx] | self.tile_data[idx + 1] << 8

    def set_tile_value(
        self, x: int, y: int, tile: int, palette: int, h_flip: bool = False, v_flip: bool = False
    ) -> None:
        idx = (y * MINIMAP_WIDTH + x) * 2
        if idx >= len(self.tile_data):
            raise IndexError(f"Tile coordinate ({x}, {y}) is not within minimap")
        value = tile | (palette << 12)
        if h_flip:
            value |= 1 << 10
        if v_flip:
            value |= 1 << 11
        self.tile_data[idx] = value & 0xFF
        self.tile_data[idx + 1] = value >> 8

    def write(self) -> None:
        comp_data = comp_lz77(self.tile_data)
        comp_len = len(comp_data)
        if comp_len > self.comp_len:
            # Repoint data
            addr = self.rom.reserve_free_space(comp_len + 2)
            self.rom.write_ptr(self.pointer, addr)
        else:
            addr = self.rom.read_ptr(self.pointer)
        self.rom.write_bytes(addr, comp_data)
        self.comp_len = comp_len


def apply_minimap_edits(rom: Rom, edit_dict: dict) -> None:
    # Go through every minimap
    for map_id, changes in edit_dict.items():
        with Minimap(rom, int(map_id)) as minimap:
            for change in changes:
                minimap.set_tile_value(
                    change["X"],
                    change["Y"],
                    change["Tile"],
                    change["Palette"],
                    change.get("HFlip", False),
                    change.get("VFlip", False),
                )
