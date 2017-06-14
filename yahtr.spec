# -*- mode: python -*-
# flake8: noqa

from kivy.deps import sdl2, glew

block_cipher = None

added_files = [
         ( 'data', 'data' ),
         ( 'yahtr\\ui\\kv', 'yahtr\\ui\\kv' )
        ]

options = [ ('--size=1280x800', None, 'OPTION') ]

a = Analysis(['yahtr\\main.py'],
             pathex=['.'],
             binaries=[],
             datas=added_files,
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
          options,
          exclude_binaries=True,
          name='yahtr',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='yahtr')
