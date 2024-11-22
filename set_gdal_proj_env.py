import os
import sys
from pathlib import Path


def get_bundled_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    else:
        return Path(relative_path)


# Set GDAL_DATA and PROJ_LIB environment variables
GDAL_DATA = get_bundled_path("GDAL_DATA")
PROJ_LIB = get_bundled_path("PROJ_LIB")
os.environ["GDAL_DATA"] = str(GDAL_DATA)
os.environ["PROJ_LIB"] = str(PROJ_LIB)