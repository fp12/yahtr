# -*- mode: python -*-

from kivy.deps import sdl2, glew

block_cipher = None

added_data = [ ('..\\data\\actions_trees\\chess_demo\\*.txt', 'data\\actions_trees\\chess_demo\\' ),
               ('..\\data\\battle_setups\\*.json', 'data\\battle_setups\\' ),
               ('..\\data\\boards\\chess_demo\\*.json', 'data\\boards\\chess_demo\\' ),
               ('..\\data\\img\\*.png', 'data\\img\\' ),
               ('..\\data\\loc\\*.*', 'data\\loc\\' ),
               ('..\\data\\skills\\chess_demo\\*.json', 'data\\skills\\chess_demo\\' ),
               ('..\\data\\templates\\units\\chess_demo\\*.json', 'data\\templates\\units\\chess_demo\\' ),
               ('..\\data\\templates\\weapons\\chess_demo\\*.json', 'data\\templates\\weapons\\chess_demo\\'),
               ('..\\yahtr\\ui\\kv\\*.kv', 'yahtr\\ui\\kv\\')]

options = [ ('--size=1280x800', None, 'OPTION') ]

a = Analysis(['..\\yahtr\\main.py'],
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
