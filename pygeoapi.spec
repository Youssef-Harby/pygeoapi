# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
import platform

# Detect MAMBA_ROOT_PREFIX
MAMBA_ROOT_PREFIX = Path(os.environ.get('MAMBA_ROOT_PREFIX', 'C:/Users/runneradmin/micromamba'))
env_name = 'pygeoapi'

if platform.system() == 'Windows':
    GDAL_DATA = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'Library' / 'share' / 'gdal'
    PROJ_LIB = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'Library' / 'share' / 'proj'
    GDAL_PLUGINS = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'Library' / 'bin' / 'gdalplugins'
    PYGEOFILTER = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'Lib' / 'site-packages' / 'pygeofilter' / 'parsers'
else:
    GDAL_DATA = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'share' / 'gdal'
    PROJ_LIB = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'share' / 'proj'
    GDAL_PLUGINS = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'lib' / 'gdalplugins'
    PYGEOFILTER = MAMBA_ROOT_PREFIX / 'envs' / env_name / 'lib' / 'python3.11' / 'site-packages' / 'pygeofilter' / 'parsers'

a = Analysis(
    ['pygeoapi/__init__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('pygeoapi/', 'pygeoapi'),
        (PYGEOFILTER / 'ecql' / 'grammar.lark', 'pygeofilter/parsers/ecql'),
        (PYGEOFILTER / 'wkt.lark', 'pygeofilter/parsers'),
        (PYGEOFILTER /'iso8601.lark', 'pygeofilter/parsers'),
        (str(GDAL_DATA), 'GDAL_DATA'),
        (str(PROJ_LIB), 'PROJ_LIB')
        ],
    hiddenimports=[
        'rasterio',
        'rasterio.rio',
        'rasterio.abc',
        'rasterio.control',
        'rasterio.coords',
        'rasterio.drivers',
        'rasterio.dtypes',
        'rasterio.enums',
        'rasterio.env',
        'rasterio.errors',
        'rasterio.features',
        'rasterio.fill',
        'rasterio.io',
        'rasterio.mask',
        'rasterio.merge',
        'rasterio.path',
        'rasterio.plot',
        'rasterio.profiles',
        'rasterio.rpc',
        'rasterio.sample',
        'rasterio.session',
        'rasterio.shutil',
        'rasterio.stack',
        'rasterio.tools',
        'rasterio.transform',
        'rasterio.vrt',
        'rasterio.warp',
        'rasterio.windows',
        'tinydb',
        'osgeo.gdal',
        'osgeo.osr',
        'osgeo.ogr',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['set_gdal_proj_env.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
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
