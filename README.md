# Metroid Advance Randomizer System Patcher

Running from source:
- Create a venv: `python -m venv venv`
- Activate the venv:
  - Windows: `call venv\scripts\activate`
  - Unix-based: `source ./venv/bin/activate`
- Install the project as editable: `pip install -e .`
- Run: `python -m mars_patcher`

Before running the patcher, you want to initialize the required assembly patches into `src/mars_patcher/data/patches/mf_u/asm`.
The easiest way to do that is by running `python pull-assembly-patches.py`, which will fetch the patches from the correct release.
However for development purposes, you may want to create the assembly patches yourself manually and then copy them to that directory.
