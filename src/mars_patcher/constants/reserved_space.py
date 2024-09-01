# Reserved Space is space in the rom that the base patch specifically has reserved for easy patcher modifications.

class ReservedConstants:
    # These need to be kept in sync with the base patch
    # found somewhere around https://github.com/MetroidAdvRandomizerSystem/MARS-Fusion/blob/main/src/main.s#L45
    MINOR_LOCS_TABLE_ADDR = 0x7FF000
    MAJOR_LOCS_ADDR = 0x7FF01C
    TANK_INC_ADDR = 0x7FF046

    # TODO: patch uses this variable for showing messages boxes more nicely. implement this.
    TOTAL_METROID_COUNT_ADDR = 0x7FF04C
    REQUIRED_METROID_COUNT_ADDR = 0x7FF04D
    STARTING_LOCATION_ADDR = 0x7FF04E
    CREDITS_END_DELAY_ADDR = 0x7FF056   # TODO: is this meant to be changed?
    CREDITS_SCROLL_SPEED_ADDR = 0x7FF058    # TODO: ditto
    HINT_SECURITY_LEVELS_ADDR = 0x7FF059    # TODO: ???
    ENVIRONMENTAL_HARZARD_DAMAGE_ADDR = 0x7FF065    # TODO: implement this
    MISSILE_LIMIT_ADDR = 0x7FF06A
    MINOR_LOCS_ARRAY_ADDR = 0x7FF06C
