from kivy.utils import platform
from kivy.config import Config
from kivy.logger import Logger

import configparser
from pathlib import Path
import os

"""
This code must be at the top of the 'main' executable file.  

"""

# Default window size and position, also used to set minimum window size
window_width = 800
window_height = 375
window_top = 50
window_left = 100

if platform == 'win':
    ini_file = Path(os.environ['APPDATA']) / Path('backingtrackplayer') / 'backingtrackplayer.ini'
else:  # macosx
    ini_file = Path('~/Library/Application Support/backingtrackplayer/backingtrackplayer.ini').expanduser()

# Use Python lib configparser to read .ini file prior to app startup
parser = configparser.ConfigParser()
try:
    found = parser.read(ini_file)  # created in main.py: build_config()
except configparser.Error as e:
    Logger.exception(f'Invalid Configuration File: {e}')
    p = Path(ini_file)
    if p.exists():
        p.unlink()
    found = False

if found:
    Config.set('graphics', 'width', parser['Window']['width'])
    Config.set('graphics', 'height', parser['Window']['height'])
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'top', parser['Window']['top'])  # find top and left
    Config.set('graphics', 'left', parser['Window']['left'])
else:
    Config.set('graphics', 'width', window_width)  # default value. match values in main.py: build_config, on_start
    Config.set('graphics', 'height', window_height)
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'top', window_top)
    Config.set('graphics', 'left', window_left)

if platform == 'macosx':
    Config.set('kivy', 'window_icon', 'icons8-refresh-512.png')
else:
    Config.set('kivy', 'window_icon', 'icons8-refresh-64.png')  # Windows uses a small png
Config.set('kivy', 'exit_on_escape', 0)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
