# -*- mode: python -*-

from kivy.deps import sdl2, glew

block_cipher = None

added_data = [ ('..\\data\\img\\*.png', 'data\\img\\' ),
               ('..\\data\\maps\\*.json', 'data\\maps\\' ),
               ('..\\data\\skills\\*.json', 'data\\skills\\' ),
               ('..\\data\\templates\\units\\*.json', 'data\\templates\\units\\' ),
               ('..\\data\\templates\\weapons\\*.json', 'data\\templates\\weapons\\'),
               ('..\\src\\ui\\kv\\*.kv', 'src\\ui\\kv\\')]

options = [ ('--size=1280x800', None, 'OPTION') ]

a = Analysis(['..\\src\\main.py'],
             pathex=['.'],
             binaries=None,
             datas=added_data,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          options,
          exclude_binaries=True,
          name='yathr',
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
               name='yathr')
