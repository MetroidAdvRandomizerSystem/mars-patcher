import random
from typing import Dict, List

from mars_patcher.constants.enemies import ENEMY_TYPES, EnemyType
from mars_patcher.constants.game_data import sprite_vram_sizes, spriteset_count, spriteset_ptrs
from mars_patcher.rom import Rom


def randomize_enemies(rom: Rom) -> None:
    # Setup enemy types dictionary
    enemy_types = {k: v[1] for k, v in ENEMY_TYPES.items()}

    # Get graphics info for each enemy
    size_addr = sprite_vram_sizes(rom)
    gfx_rows = {}
    for en_id in enemy_types:
        size = rom.read_32(size_addr + (en_id - 0x10) * 4)
        gfx_rows[en_id] = size // 0x800

    # Get replacement pools
    replacements: Dict[EnemyType, List[int]] = {t: [] for t in EnemyType}
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

    # Randomize spritesets
    ss_ptrs = spriteset_ptrs(rom)
    for i in range(spriteset_count(rom)):
        spriteset_addr = rom.read_ptr(ss_ptrs + i * 4)
        used_gfx_rows: Dict[int, int] = {}
        for j in range(0xF):
            addr = spriteset_addr + j * 2
            en_id = rom.read_8(addr)
            if en_id == 0:
                break
            if en_id not in enemy_types:
                continue

            # Check if sprite shares graphics with another
            gfx_row = rom.read_8(addr + 1)
            if gfx_row in used_gfx_rows:
                new_id = used_gfx_rows[gfx_row]
                rom.write_8(addr, new_id)
                continue

            # Choose randomly and assign
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
