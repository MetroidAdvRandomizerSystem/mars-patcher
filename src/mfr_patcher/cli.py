import argparse

from mfr_patcher.patcher import patch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("rom_path", type=str, help="Path to a GBA ROM file")
    parser.add_argument("out_path", type=str, help="Path to output ROM file")
    parser.add_argument("patch_data_path", type=str, help="Path to patch data json file")
    args = parser.parse_args()

    patch(args.rom_path,
          args.out_path,
          args.patch_data_path,
          lambda progress, message: print(message)
          )
