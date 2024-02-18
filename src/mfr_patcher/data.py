import os
from pathlib import Path

def get_data_path() -> str:
    return os.fspath(Path(__file__).parent.joinpath("data") )


