class ReservedConstants:
    """
    These are constants that are in the patches 'Reserved Space';
    things that are intended to be modified by this patcher.
    """

    # These need to be kept in sync with the base patch
    # found somewhere around https://github.com/MetroidAdvRandomizerSystem/MARS-Fusion/blob/main/src/main.s#L45
    MINOR_LOCS_TABLE_ADDR = 0x7FF000
    MAJOR_LOCS_ADDR = 0x7FF01C
    TANK_INC_ADDR = 0x7FF046
    TOTAL_METROID_COUNT_ADDR = 0x7FF04C
    REQUIRED_METROID_COUNT_ADDR = 0x7FF04D
    STARTING_LOCATION_ADDR = 0x7FF04E
    CREDITS_END_DELAY_ADDR = 0x7FF056  # TODO: Is this meant to be changed?
    CREDITS_SCROLL_SPEED_ADDR = 0x7FF058  # TODO: Ditto
    HINT_SECURITY_LEVELS_ADDR = 0x7FF059  # TODO: ???
    ENVIRONMENTAL_HARZARD_DAMAGE_ADDR = 0x7FF065  # TODO: Implement this
    MISSILE_LIMIT_ADDR = 0x7FF06A
    MINOR_LOCS_ARRAY_ADDR = 0x7FF06C
    # Pointers, offset by language value, that store the message table location
    MESSAGE_TABLE_LOOKUP_ADDR = 0x79CDF4
    FIRST_CUSTOM_MESSAGE_ID = 0x38  # The first 0x37 messages are reserved for standard messages
