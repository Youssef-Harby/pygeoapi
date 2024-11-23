# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
import platform
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# Detect MAMBA_ROOT_PREFIX
MAMBA_ROOT_PREFIX = Path(os.environ.get('MAMBA_ROOT_PREFIX', 'C:/Users/runneradmin/micromamba'))
env_name = 'pygeoapi'

# Define GDAL, PROJ, and other necessary paths
if platform.system() == 'Windows':
    pathex = [str(MAMBA_ROOT_PREFIX / 'envs' / env_name / 'Lib' / 'site-packages')]
    GDAL_DATA = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'Library' / 'share' / 'gdal'
    PROJ_LIB = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'Library' / 'share' / 'proj'
    GDAL_PLUGINS = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'Library' / 'bin' / 'gdalplugins'
    PYGEOFILTER = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'Lib' / 'site-packages' / 'pygeofilter' / 'parsers'
else:
    pathex = [str(MAMBA_ROOT_PREFIX / 'envs' / env_name / 'lib' / f'python{platform.python_version_tuple()[0]}.{platform.python_version_tuple()[1]}' / 'site-packages')]
    GDAL_DATA = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'share' / 'gdal'
    PROJ_LIB = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'share' / 'proj'
    GDAL_PLUGINS = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'lib' / 'gdalplugins'
    PYGEOFILTER = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'lib' / f'python{platform.python_version_tuple()[0]}.{platform.python_version_tuple()[1]}' / 'site-packages' / 'pygeofilter' / 'parsers'

# Collect all pygeoapi and rasterio submodules dynamically
pygeoapi_submodules = collect_submodules('pygeoapi')
rasterio_submodules = collect_submodules('rasterio')

# Collect GDAL, PROJ, and rasterio data files
gdal_data_files = collect_data_files('osgeo', subdir='data/gdal')
proj_data_files = collect_data_files('osgeo', subdir='data/proj')
rasterio_data_files = collect_data_files('rasterio')
dynamic_libs = collect_dynamic_libs('rasterio')

# Collect all pygeoapi data files
pygeoapi_data_files = collect_data_files('pygeoapi', include_py_files=True)

# Create the Analysis object
a = Analysis(
    ['pygeoapi/__init__.py'],  # Entry script
    pathex=pathex,
    binaries=dynamic_libs,
    datas=[
        *pygeoapi_data_files,  # Include all pygeoapi files
        *rasterio_data_files,  # Include rasterio data files
        (PYGEOFILTER / 'ecql' / 'grammar.lark', 'pygeofilter/parsers/ecql'),
        (PYGEOFILTER / 'wkt.lark', 'pygeofilter/parsers'),
        (PYGEOFILTER / 'iso8601.lark', 'pygeofilter/parsers'),
        *gdal_data_files,
        *proj_data_files,
    ],
    hiddenimports=[
        *pygeoapi_submodules,  # Include all pygeoapi submodules
        *rasterio_submodules,  # Include all rasterio submodules
        'tinydb',
        'osgeo.gdal',
        'osgeo.osr',
        'osgeo.ogr',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['set_gdal_proj_env.py'],  # GDAL/PROJ environment variables
    excludes=[],
    noarchive=False,
    optimize=0,
)

# Create the PyInstaller executables
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pygeoapi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='pygeoapi-bin-icon.png',
)
