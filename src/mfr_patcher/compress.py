from typing import Tuple


def decomp_rle(input: bytes, idx: int) -> Tuple[bytearray, int]:
    """
    Decompresses RLE data and returns it with the size of the compressed data.
    """
    src_start = idx
    passes = bytearray()
    # for each pass
    for p in range(2):
        if p == 1:
            half = len(passes)
        num_bytes = input[idx]
        idx += 1
        while True:
            amount = None
            compare = None
            if num_bytes == 1:
                amount = input[idx]
                compare = 0x80
            else:
                # num_bytes == 2
                amount = (input[idx] << 8) | input[idx + 1]
                compare = 0x8000
            idx += num_bytes

            if amount == 0:
                break

            if (amount & compare) != 0:
                # compressed
                amount %= compare
                val = input[idx]
                idx += 1
                while amount > 0:
                    passes.append(val)
                    amount -= 1
            else:
                # uncompressed
                while amount > 0:
                    passes.append(input[idx])
                    idx += 1
                    amount -= 1

    # each pass must be equal length
    if len(passes) != half * 2:
        raise ValueError()

    # combine passes to get output
    output = bytearray()
    for i in range(half):
        output.append(passes[i])
        output.append(passes[half + i])

    # return bytes and compressed size
    comp_size = idx - src_start
    return output, comp_size


def comp_rle(input: bytes) -> bytearray:
    """
    Compresses data using RLE.
    """

    # inner helper functions
    def write_len(arr: bytearray, val: int, size: int) -> None:
        if size == 0:
            arr.append(val)
        else:
            arr.append(val >> 8)
            arr.append(val & 0xFF)

    def add_unique(arr: bytearray, unique: bytearray, size: int) -> None:
        write_len(arr, len(unique), size)
        arr += unique
        unique.clear()

    output = bytearray()
    # do two passes for low and high bytes
    for p in range(2):
        # get counts of consecutive values
        values = bytearray()
        counts = []

        prev = input[p]
        values.append(prev)
        count = 1

        for i in range(p + 2, len(input), 2):
            val = input[i]
            if val == prev:
                count += 1
            else:
                values.append(val)
                counts.append(count)
                prev = val
                count = 1
        counts.append(count)

        # try each read length (1 or 2)
        shortest: bytearray | None = None
        for r in range(2):
            temp = bytearray()
            min_run_len = 3 + r
            flag = 0x80 << (8 * r)
            max_run_len = flag - 1
            unique = bytearray()

            # write number of bytes to read
            temp.append(r + 1)

            # for each value and its count
            for i in range(len(values)):
                count = counts[i]
                # if the value's count is long enough for a run
                if count >= min_run_len:
                    # if the value is preceded by unique values
                    if len(unique) > 0:
                        add_unique(temp, unique, r)
                    # add run length and value (multiple times if over max run length)
                    while count > 0:
                        curr_len = min(count, max_run_len)
                        len_flag = curr_len + flag
                        write_len(temp, len_flag, r)
                        temp.append(values[i])
                        count -= curr_len
                # if the value's count is too short for a run
                else:
                    # if the total count would be too long for a run
                    if len(unique) + count > max_run_len:
                        add_unique(temp, unique, r)
                    for _ in range(count):
                        unique.append(values[i])
            # check if there were unique values at the end
            if len(unique) > 0:
                add_unique(temp, unique, r)
            # write ending zero(s)
            temp.append(0)
            if r == 1:
                temp.append(0)
            if shortest is None or len(temp) < len(shortest):
                shortest = temp
        if shortest is None:
            raise ValueError()
        output += shortest
    return output
