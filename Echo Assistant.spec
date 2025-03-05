# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('src/echo', 'echo')]
binaries = []
hiddenimports = ['numpy', 'numpy.core._dtype_ctypes', 'numpy.fft', 'echo.voice_assistant', 'echo.utils.notifications', 'echo.services.transcriber', 'echo.services.openai_service', 'av', 'av.filter', 'av.filter.graph', 'av.audio.codeccontext', 'faster_whisper']
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('av')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('faster_whisper')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['src/echo/main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='Echo Assistant',
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
    icon=['/Users/pz-personal-macbook-pro/Documents/dev/echo/src/echo/assets/icons/echo.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Echo Assistant',
)
app = BUNDLE(
    coll,
    name='Echo Assistant.app',
    icon='/Users/pz-personal-macbook-pro/Documents/dev/echo/src/echo/assets/icons/echo.png',
    bundle_identifier=None,
)
