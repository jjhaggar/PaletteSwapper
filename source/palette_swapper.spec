# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['palette_swapper.py'],
    pathex=[],
    binaries=[],
# Change the following paths with the ones that contains the files in your computer
    datas=[ 
		('D:/PALETTECHANGER/my_venv/Lib/site-packages/tkinterdnd2/tkdnd/win-x64/libtkdnd2.9.4.dll', 'tkdnd'),
		('D:/PALETTECHANGER/my_venv/Lib/site-packages/tkinterdnd2/tkdnd/win-x64/*.tcl', 'tkdnd'),
	],
    hiddenimports=['tkinterdnd2.tkinterdnd'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='palette_swapper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
	icon='palette_swapper_icon.ico',
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
