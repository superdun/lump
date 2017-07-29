# -*- mode: python -*-

block_cipher = None


a = Analysis(['twelve.py'],
             pathex=['C:\\Users\\lidad\\Desktop\\opt\\lump'],
             binaries=[],
             datas=[("save/*","save"),("imgs/*","imgs")],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='twelve',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon="imgs/logo.ico")
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='twelve')
