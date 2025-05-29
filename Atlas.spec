# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Add the root directory to Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

a = Analysis(
    ['gui/app.py'],
    pathex=[os.path.dirname(os.path.abspath('.'))],
    binaries=[
        ('drivers/chromedriver.exe', 'drivers'),
        (r'C:\Program Files\Google\Chrome\Application\chrome.exe', 'chrome')
        # Add Chrome binary if needed (check your Chrome installation path)
        # (r'C:\Program Files\Google\Chrome\Application\chrome.exe', 'chrome')
    ],
    datas=[
        ('assets/atlas.ico', 'assets'),
        ('src', 'src'),
        ('gui', 'gui')
    ],
    hiddenimports=[
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.common',
        'selenium.webdriver.common.by',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'docx',
        'PIL',
        'imagehash'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Atlas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep True for debugging, set to False later
    icon='assets/atlas.ico',
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)