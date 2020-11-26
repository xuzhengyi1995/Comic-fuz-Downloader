import json
import sys
from copy import deepcopy
from pathlib import Path

from comicfuz_downloader_core import *


def main():
    # Check whether the script is packed
    if getattr(sys, 'frozen', False):
        # If the script is packed by PyInstaller, value of sys.executable is path to the packed executable
        file_root = Path(sys.executable).parent
    else:
        file_root = Path(__file__).parent

    config_path = file_root / 'gui-config.json'
    icon_path = file_root / 'assets' / 'logo-icon.ico'

    icon_path_str = str(icon_path) if icon_path.exists() else ''

    try:
        config_raw = json.loads(config_path.read_text())
        config = deepcopy(DEFAULT_CONFIG)
        config.update(config_raw)
    except:
        config = DEFAULT_CONFIG

    while True:
        main_form = MainForm(config, icon_path_str)
        config, should_restart = main_form.main_loop()
        config_path.write_text(json.dumps(config), encoding='utf-8')
        if not should_restart:
            break


if __name__ == '__main__':
    main()
