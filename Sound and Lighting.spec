# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['env/bin', 'env/lib/python3.10/site-packages'],
    binaries=[],
    datas=[('Contents/Documents', 'Contents/Documents'), ('Contents/images', 'Contents/images'), ('Contents/Recordings', 'Contents/Recordings'), ('Contents/.temp', 'Contents/.temp'), ('Contents/TestDatabase.db', 'Contents'), ('Contents/agsStyle.json' , 'Contents')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Sound and Lighting',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='Contents',
    icon=['Contents/images/ags.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Sound and Lighting',
)
app = BUNDLE(
    coll,
    name='Sound and Lighting.app',
    icon='Contents/images/ags.png',
    bundle_identifier=None,
)
