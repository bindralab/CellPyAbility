# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['CellPyAbilityGUI.py'],
    pathex=['.'],
    binaries=[],
    datas=[
    ('CellPyAbilityLogo.png', '.'),
    ('CellPyAbilityIcon.ico', '.'),
    ('CellPyAbility.cppipe', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CellPyAbility',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['CellPyAbilityIcon.ico'],
)
