from enum import Enum
import json
import random

from mfr_patcher.data import get_data_path
from mfr_patcher.rom import Rom


class EnemyType(Enum):
    CRAWLING = 1
    GROUND = 2
    CEILING = 3
    GROUND_CEILING = 4
    WALL = 5
    FLYING = 6


TYPE_ENUMS = {
    "Crawling": EnemyType.CRAWLING,
    "Ground": EnemyType.GROUND,
    "Ceiling": EnemyType.CEILING,
    "GroundCeiling": EnemyType.GROUND_CEILING,
    "Wall": EnemyType.WALL,
    "Flying": EnemyType.FLYING
}


def randomize_enemies(rom: Rom):
    # setup enemy types dictionary
    with open(get_data_path("enemy_types.json")) as f:
        data = json.load(f)
    enemy_types = {d["ID"]: TYPE_ENUMS[d["Type"]] for d in data}
    
    # get graphics info for each enemy
    size_addr = rom.sprite_vram_size_addr()
    gfx_rows = {}
    for en_id in enemy_types:
        size = rom.read_32(size_addr + (en_id - 0x10) * 4)
        gfx_rows[en_id] = size // 0x800

    # get replacement pools
    replacements = {t: [] for t in EnemyType}
    for en_id, en_type in enemy_types.items():
        replacements[en_type].append(en_id)
        if en_type == EnemyType.CRAWLING:
            replacements[EnemyType.GROUND].append(en_id)
            replacements[EnemyType.CEILING].append(en_id)
            replacements[EnemyType.GROUND_CEILING].append(en_id)
            replacements[EnemyType.WALL].append(en_id)
        elif en_type == EnemyType.GROUND_CEILING:
            replacements[EnemyType.GROUND].append(en_id)
            replacements[EnemyType.CEILING].append(en_id)
        # Ground, Ceiling, Wall, and Flying cannot replace others
    
    # randomize spritesets
    spriteset_ptrs = rom.spriteset_addr()
    for i in range(rom.spriteset_count()):
        spriteset_addr = rom.read_ptr(spriteset_ptrs + i * 4)
        used_gfx_rows = {}
        for j in range(0xF):
            addr = spriteset_addr + j * 2
            en_id = rom.read_8(addr)
            if en_id == 0:
                break
            if en_id not in enemy_types:
                continue

            # check if sprite shares graphics with another
            gfx_row = rom.read_8(addr + 1)
            if gfx_row in used_gfx_rows:
                new_id = used_gfx_rows[gfx_row]
                rom.write_8(addr, new_id)
                continue

            # choose randomly and assign
            en_type = enemy_types[en_id]
            candidates = replacements[en_type]
            random.shuffle(candidates)
            for new_id in candidates:
                new_row_count = gfx_rows[new_id]
                row_count = gfx_rows[en_id]
                if new_row_count <= row_count:
                    rom.write_8(addr, new_id)
                    used_gfx_rows[gfx_row] = new_id
                    break
