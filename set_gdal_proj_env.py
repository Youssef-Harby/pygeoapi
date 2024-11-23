import os
import sys
from pathlib import Path


def get_bundled_path(relative_path):
    """
    Returns the path to a bundled resource, or the fallback relative path if
    not in a bundled environment.
    """
    if hasattr(sys, "_MEIPASS"):  # PyInstaller sets _MEIPASS during runtime
        return Path(sys._MEIPASS) / relative_path
    else:
        return Path(relative_path)


# Attempt to locate bundled directories
GDAL_DATA = get_bundled_path("GDAL_DATA")
PROJ_LIB = get_bundled_path("PROJ_LIB")
GDAL_PLUGINS = get_bundled_path("GDAL_PLUGINS")

# Debug: Print paths for verification
print(f"GDAL_DATA path: {GDAL_DATA}")
print(f"PROJ_LIB path: {PROJ_LIB}")
print(f"GDAL_PLUGINS path: {GDAL_PLUGINS}")

# Verify paths exist before setting them
if GDAL_DATA.exists():
    os.environ["GDAL_DATA"] = str(GDAL_DATA)
else:
    print(f"Warning: GDAL_DATA directory not found at {GDAL_DATA}")

if PROJ_LIB.exists():
    os.environ["PROJ_LIB"] = str(PROJ_LIB)
else:
    print(f"Warning: PROJ_LIB directory not found at {PROJ_LIB}")

if GDAL_PLUGINS.exists():
    os.environ["GDAL_PLUGINS"] = str(GDAL_PLUGINS)
else:
    print(f"Warning: GDAL_PLUGINS directory not found at {GDAL_PLUGINS}")

# Debug: Print final environment variables
print(f"Environment GDAL_DATA: {os.environ.get('GDAL_DATA')}")
print(f"Environment PROJ_LIB: {os.environ.get('PROJ_LIB')}")
print(f"Environment GDAL_PLUGINS: {os.environ.get('GDAL_PLUGINS')}")
