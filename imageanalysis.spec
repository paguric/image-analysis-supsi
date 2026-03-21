from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('imageio')

a = Analysis(
    ['backend/app/main.py'],
    pathex=['.'],
    datas=[
        ('frontend/dist', 'static'),
    ],
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
        'imageio',
        'imageio.plugins.freeimage',
        'imageio.plugins.ffmpeg',
    ],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas,
    name='SUPSI Image Analysis',
    onefile=True,
    windowed=True,
    console=False,
)
