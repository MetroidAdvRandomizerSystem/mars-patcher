import argparse
import copy
import json
import typing

from mars_patcher.auto_generated_types import MarsSchema
from mars_patcher.patcher import patch, validate_patch_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom_path", type=str, help="Path to a GBA ROM file")
    parser.add_argument("out_path", type=str, help="Path to output ROM file")
    parser.add_argument("patch_data_path", type=str, help="Path to patch data json file")
    args = parser.parse_args()

    # Load patch data file and validate
    with open(args.patch_data_path) as f:
        patch_data = json.load(f)

    validate_patch_data(patch_data)

    patch(
        args.rom_path,
        args.out_path,
        typing.cast(MarsSchema, copy.copy(patch_data)),
        lambda message, progress: print(message),
    )
