# Title:    Stremio Windows Build Script
# Author:   ShoobyDoo
# Date:     2023-03-13
# Edited:   2023-03-18
# Version:  0.1.0

import os
import sys
from pprint import pprint
import time

# append the core directory to the path so we can import from it
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), 'abs\\core\\')))
from abs.core.helpers import Helpers
from abs.core.depends import Depends


def main():
    Helpers.cls()
    print("------------------------------ [Automatic Build Script for Stremio] ------------------------------")

    try:
        dp = Depends()

        print("[Checking Config]\n")
        if dp.cfg_path:
            dp.depend_paths = dp.read_config()['DEPENDS']
            pprint(dp.depend_paths)

        else:
            print("No config found. Starting first time startup procedure...\n\n[Checking Dependencies]\n")

            # check git
            dp.check_depend("git --version", "Git", dp.GIT_URL)

            # check qt
            dp.check_depend("windeployqt.exe --version", "Qt", dp.QT_URL)

            # check openssl
            dp.check_depend(["openssl", "version"], "OpenSSL", dp.OSSL_URL)

            # check nodejs
            dp.check_depend("node --version", "NodeJS", dp.NODEJS_URL)

            # check ffmpeg
            dp.check_depend("ffmpeg --version", "FFMpeg", dp.FFMPEG_URL)

            # check libmpv
            dp.check_depend("mpv placeholder", "MPV", dp.LIBMPV_URL)

            # check visual studio 2017
            dp.check_depend("vs placeholder", "VS_Community", dp.VSCOMM_URL)

            # check cmake
            dp.check_depend("cmake --version", "CMake", dp.CMAKE_URL)

            print("\n[Checking Dependencies Complete]")

            # Write to config
            dp.write_config()
        
        print("\n[Config Complete]\n")
        ynp = Helpers.yes_no_prompt("Build Stremio?")
        
        if ynp:
            dp.build_stremio()
            # print("Stremio built successfully.")
            # time.sleep(2)
            # main()

    except KeyboardInterrupt:
        print("[DEBUG]")
        ynp = Helpers.yes_no_prompt("Reset/delete config?")
        if ynp:
            dp.reset_config('abs/abs.json')
            print("Config deleted. Program will now restart...")
            time.sleep(2)
            main()

if __name__ == '__main__':
    main()
