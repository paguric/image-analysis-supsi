from PyInstaller.utils.hooks import collect_all, copy_metadata

# Recuperiamo tutto ciò che serve per imageio (file, binari e moduli nascosti)
img_datas, img_binaries, img_hidden = collect_all('imageio')

a = Analysis(
    ['backend/app/main.py'],
    pathex=['.'],
    datas=[
        ('frontend/dist', 'static'),
    ] + img_datas + copy_metadata('imageio'), # Aggiunti i metadati per evitare l'errore PackageNotFoundError
    binaries=img_binaries,
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'webview',
    ] + img_hidden, # Uniamo gli hidden imports rilevati automaticamente
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='SUPSI Image Analysis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Impostato su False per non mostrare il terminale
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
    windowed=True,
)