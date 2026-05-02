from PyInstaller.utils.hooks import collect_all, copy_metadata

img_datas, img_binaries, img_hidden = collect_all('imageio')

a = Analysis(
    ['backend/app/main.py'],
    pathex=['.'],
    datas=[
        ('frontend/dist', 'frontend/dist'),  # deve matchare static_dir in main.py
    ] + img_datas + copy_metadata('imageio'),
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
        'multipart',
        'sqlmodel',
        'sqlalchemy',
        'sqlalchemy.dialects.sqlite',
        'webview',
    ] + img_hidden,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='SUPSI Image Analysis',
    onefile=True,
    windowed=True,
    console=False,
    icon='assets/icon.ico'
)