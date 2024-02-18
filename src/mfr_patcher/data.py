import os
from pathlib import Path
from typing import Tuple


def get_data_path(*path: Tuple[str, ...]) -> str:
    return os.fspath(Path(__file__).parent.joinpath("data", *path))
