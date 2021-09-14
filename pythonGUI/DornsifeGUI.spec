# -*- mode: python -*-

block_cipher = None


a = Analysis(['DornsifeGUI.py'],
             pathex=['C:\\Python3.5\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'C:\\cygwin64\\home\\craig\\dornsife_backend\\pythonGUI'],
             binaries=[],
             datas=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='DornsifeGUI',
          debug=False,
          strip=False,
          upx=True,
          console=True )
