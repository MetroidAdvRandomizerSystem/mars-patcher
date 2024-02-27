import os
from pathlib import Path
from typing import Tuple


def get_data_path(*path: str | os.PathLike) -> str:
    return os.fspath(Path(__file__).parent.joinpath("data", *path))
