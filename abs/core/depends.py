# Title:    Stremio Windows Build Script
# Author:   ShoobyDoo
# Date:     2023-03-13
# Edited:   2023-03-18
# Version:  0.1.0

import os
import sys
import glob
import string
import time
import json
import subprocess
import shutil

from pprint import pprint
from typing import Union
from ctypes import windll

from helpers import Helpers


class Depends:
    def __init__(self):
        # [---------------------------------------------------------BUILD DEPENDENCIES---------------------------------------------------------] #
        #  Git version: latest as of 2023-03-15
        self.GIT_URL = "https://github.com/git-for-windows/git/releases/download/v2.39.2.windows.1/Git-2.39.2-64-bit.exe"

        #  Qt version: 5.12.7 x86 (indicated by Stremio)
        self.QT_URL = "https://qt.mirror.constant.com/archive/qt/5.12/5.12.7/qt-opensource-windows-x86-5.12.7.exe"

        #  OpenSSL version: 1.1.1 32bit (indicated by Stremio)
        self.OSSL_URL = "https://slproweb.com/download/Win32OpenSSL-1_1_1t.exe"

        #  NodeJS version: 8.17.0 x86 (indicated by Stremio)
        self.NODEJS_URL = "https://nodejs.org/dist/v8.17.0/win-x86/node.exe"

        #  FFMPEG version: 3.3.4 32 bit (indicated by Stremio) (Prefaced by: Other versions may also work)
        self.FFMPEG_URL = "https://github.com/GyanD/codexffmpeg/releases/download/4.3.1-2020-11-08/ffmpeg-4.3.1-2020-11-08-full_build-shared.zip"

        #  MPV version: latest (dev-i686 indicated by Stremio) as of 2023-03-15
        self.LIBMPV_URL = "https://master.dl.sourceforge.net/project/mpv-player-windows/libmpv/mpv-dev-i686-20230312-git-9880b06.7z?viasf=1"

        #  VS Community version: 2017 (indicated by Stremio)
        self.VSCOMM_URL = "https://download.visualstudio.microsoft.com/download/pr/4de9b77e-bbd8-4a05-a083-662e1a187b94/fa117cc0e7e02d61a420803605d5723993d590269e92d5b1cd85db2e7b60d48c/vs_Community.exe"

        #  CMAKE version: latest as of 2023-03-15
        self.CMAKE_URL = "https://github.com/Kitware/CMake/releases/download/v3.26.0/cmake-3.26.0-windows-x86_64.msi"
        # [---------------------------------------------------------BUILD DEPENDENCIES---------------------------------------------------------] #

        self.drives = []
        self.depend_paths = {
            "git": "",
            "qt": "",
            "openssl": "",
            "vs_community": "",
            "nodejs": "",
            "ffmpeg": "",
            "mpv": ""
        }
        self.ljust = 50
        
        # set the path to the config file if it exists, otherwise set to None
        self.cfg_path = glob.glob('./abs/abs.json')[0] if len(glob.glob('./abs/abs.json')) > 0 else None 

        # do this in the instantiation instead of everytime we check a depend
        d_bitmask = windll.kernel32.GetLogicalDrives()
            
        for letter in string.ascii_uppercase:
            if d_bitmask & 1:
                self.drives.append(letter)
            d_bitmask >>= 1


    def check_depend(self, pgm_args: Union[str, list], pgm_name: str, pgm_url: str) -> None:
        """
        Checks if a program is installed.

        Args:
            pgm_args (str | list): The arguments to pass to the program.
            pgm_name (str): The name of the program.
            pgm_out_filename (str): The filename to save the program as.
        """

        try:
            time.sleep(0.15)
            print(f"Checking if {pgm_name} is installed...".ljust(self.ljust, '.'), end='')
            if type(pgm_args) == str:
                pgm_args = pgm_args.split()

            sp_pgm = subprocess.run(pgm_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if sp_pgm.returncode == 0:
                print(f"OK: " + sp_pgm.stdout.decode().split('\n')[0].strip())
                self.depend_paths[pgm_name.lower()] = pgm_args[0] 
        
        except FileNotFoundError:
            print(f"NO: {pgm_name} not on path...\n\nSearching default install paths on all drives...")
            self.verify_depend(pgm_name, pgm_url)


    def verify_depend(self, pgm_name: str, pgm_url: str) -> None:
        # verify depend: Git
        if pgm_name == "Git":
            self.check_path(pgm_name, pgm_url, ":\\Program Files\\Git")

        # verify depend: Qt
        # TODO: could be refactored to be more generic?
        elif pgm_name == "Qt":
            # not going to use the self.check_path() method here because it's a bit different
            qt_path_struct = ":\\Qt\\Qt5.12.7\\5.12.7"
            qt_path_struct_addons = ":\\Qt\\Qt5.12.7\\installerResources"

            for drive_letter in self.drives:
                qt_webe = glob.glob(f"{drive_letter}{qt_path_struct_addons}\\qt.qt5.5127.qtwebengine*")  # wildcard for webengine
                qt_msvc = glob.glob(f"{drive_letter}{qt_path_struct_addons}\\qt.qt5.5127.win32_msvc*")  # wildcard for msvc
                qt_msvc_bin = glob.glob(f"{drive_letter}{qt_path_struct}\\msvc*")  # wildcard for BASE_DIR/msvc/bin
                
                # check if default qt 5.12.7 install path exists "C:\Qt\Qt5.12.7\5.12.7\msvc2017\bin\"
                if len(glob.glob(f"{qt_msvc_bin[0]}\\bin\\windeployqt.exe")) > 0:
                    self.depend_paths[pgm_name.lower()] = f"{qt_msvc_bin[0]}\\bin\\windeployqt.exe"
                    print(f"Found {pgm_name}! [{self.depend_paths[pgm_name.lower()]}]\n\nVerifying Qt Addons...")
                    
                    if len(qt_webe) > 0 and len(qt_msvc) > 0:
                        print("Qt WebEngine: OK\nQt MSVC:      OK\n")
                    else:
                        print("One of the following: [Qt WebEngine, Qt MSVC (32 Bit)] were missing from your Qt installation...\nPlease correct this and try again.")
                    
                    print("Checking if Qt is installed...".ljust(self.ljust, '.') + f"OK: {self.depend_paths[pgm_name.lower()]}")
                    break
            else:
                self.depend_not_found(pgm_name, pgm_url)

        # verify depend: OpenSSL
        elif pgm_name == "OpenSSL":
            self.check_path(pgm_name, pgm_url, ":\\Program Files (x86)\\OpenSSL-Win*\\bin\\openssl.exe")

        # verify depend: NodeJS
        elif pgm_name == "NodeJS":
            self.check_path(pgm_name, pgm_url, ":\\Program Files\\nodejs\\node.exe")

        # verify depend: FFMpeg
        elif pgm_name == "FFMpeg":
            self.check_path(pgm_name, pgm_url, "ffmpeg.exe")

        # verify depend: MPV
        elif pgm_name == "MPV":
            self.check_path(pgm_name, pgm_url, ":\\Program Files\\MPV\\bin\\mpv.exe")

        # verify depend: VS Community version 2017
        elif pgm_name == "VS_Community":
            self.check_path(pgm_name, pgm_url, ":\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Community\\VC\\Auxiliary\\Build\\vcvars32.bat")
        
        # verify depend: CMake
        elif pgm_name == "CMake":
            self.check_path(pgm_name, pgm_url, ":\\Program Files\\CMake\\bin\\cmake.exe")


    def check_path(self, pgm_name: str, pgm_url: str, path_struct: str) -> None:
        """
        Checks if a specific path exists on any drive.

        Args:
            pgm_name (str): The name of the program.
            pgm_url (str): The URL to the program download.
            path_struct (str): The path structure to check.
        """

        current_drive = ""
        for drive_letter in self.drives:
            current_drive += f"{drive_letter}:\\, " if drive_letter != self.drives[-1] else f"{drive_letter}:\\"
            print(f"Checking {current_drive} for {pgm_name}...", end='\r')
            time.sleep(0.05)
            
            # if the path doesnt start with the colon, its likely a relative path
            if not path_struct.startswith(":"):
                path_to_check = glob.glob(f"{path_struct}")
            else:
                path_to_check = glob.glob(f"{drive_letter}{path_struct}")

            if len(path_to_check) > 0:
                self.depend_paths[pgm_name.lower()] = path_to_check[0]
                print(f"\n\nFound {pgm_name}! [{self.depend_paths[pgm_name.lower()]}]\n")

                # VERIFY: depending on the program, checking the versin could be --version or just version
                if pgm_name in ['OpenSSL']:
                    pgm_args = [f"{self.depend_paths[pgm_name.lower()]}", "version"]
                else:
                    pgm_args = [f"{self.depend_paths[pgm_name.lower()]}", "--version"]

                self.check_depend(pgm_args, pgm_name, pgm_url)
                break

        else:
            print('\n')
            self.depend_not_found(pgm_name, pgm_url)


    def depend_not_found(self, pgm_name: str, pgm_url: str):
        print(f"{pgm_name} not found on any drive.")

        if Helpers.ynp("Is it installed anywhere else?"):
            while True:
                pgm_path = input("Enter the path to the program: ")
                if os.path.exists(pgm_path):
                    print(f"Found {pgm_name} at: {pgm_path}")
                    break
                else:
                    print(f"Could not find {pgm_name} at: {pgm_path}")

        else:
            if Helpers.ynp("Would you like me to grab it?"):
                # have dlf return params and do the install here, so we can set the path
                dlf = Helpers.download_file(pgm_url, f"{pgm_name}.exe")
                
                # dlf returns tuple with filename and file type
                insf = Helpers.install_file(dlf[0], dlf[1])

                # if install file didnt return none
                if insf:
                    self.depend_paths[pgm_name.lower()] = insf

            else:
                print(f"Please install it manually and try again as the script may now break.\nSee: {pgm_url}")


    def get_all_paths(self) -> None:
        return self.depend_paths


    @staticmethod
    def reset_config(config_path) -> None:
        os.remove(config_path)


    def write_config(self, key = None, value = None):
        print("\nChecking for existing config...")

        if self.cfg_path and key != None:
            print("Existing config found. Reading...")
            conf = json.load(open(self.cfg_path))
            conf['DEPENDS'][key] = value
            
            print(f"Writing key/val: [{key} -> {value}] to config file...")
            json.dump(conf, open(self.cfg_path, 'w'), indent=4)
        else:
            # check to see if the abs path exists, otherwise create it
            if not os.path.exists('abs'): os.mkdir('abs')

            # generate the default config, which will be everything we've done in the program so far
            print("No configuration file was found. Generating default...")
            default = {
                'DEPENDS': self.get_all_paths()
            }

            # write the default config to the abs.json file
            json.dump(default, open('./abs/abs.json', 'w'), indent=4)


    def read_config(self, filename='abs.json', filepath = './abs/'):
        if len(glob.glob(f"{filepath}{filename}")) > 0:
            print(f"Config ({filename}) found. Reading...")
            conf = json.load(open(f'{filepath}{filename}'))
            return conf
        else:
            print("Error! No configuration file was found. Please run the script again to generate one.\n(This should never fire, reproduce this error and report it to the developer.)")


    @staticmethod
    def where_is_path_var(path_var):
        """
        Returns the path of a variable in the PATH environment variable.
        """
        for path in os.environ['PATH'].split(os.pathsep):
            if path_var in path:
                return f"{path}\\{path_var}.exe" # windows only


    def build_stremio(self):
        print("Building Stremio...\nCloning Stremio repo...")
        # subprocess.run(["git", "clone", "--recursive", "https://github.com/Stremio/stremio-shell.git"])
        print("\ndone.\n")

        print("Setting up build environment...")
        os.chdir("stremio-shell") # since we just chdir'd into stremio-shell paths get shifted -> ../{whatever} ???
        
        # # TODO: DYNAMIC CHECK, DO NOT LEAVE HARD CODED
        # sys.path.append("C:\\Qt\\Qt5.12.7\\5.12.7\\msvc2017\\bin")
        # sys.path.append("C:\\OpenSSL-Win32\\bin")

        # input(os.getcwd())
        vcvars_out = subprocess.check_output(f'"{self.depend_paths["vs_community"]}" && \
                  FOR /F "usebackq delims== tokens=2" %i IN (`type stremio.pro ^| find "VERSION=4"`) DO set package_version=%i && echo %i', shell=True)
        
        strem_ver = vcvars_out.decode('utf-8').splitlines()[-1]
        print(f"Pulled Stremio package version: {strem_ver}")
        
        serverjs_url = f"https://s3-eu-west-1.amazonaws.com/stremio-artifacts/four/v{strem_ver}/server.js"
        if not os.path.exists("server.js"): Helpers.basic_download(serverjs_url, "server.js")
        print("\ndone.\n")

        # TODO: ensure the qt5dir path is not hardcoded and automatically grabbed somewhere in the initial instantiantion of the config items
        print("Building the Stremio Shell...")
        subprocess.run(f'"{self.depend_paths["vs_community"]}" && cmake -G\"NMake Makefiles\" -DCMAKE_PREFIX_PATH="C:\\Qt\\Qt5.12.7\\5.12.7\\msvc2017\\lib\\cmake\\Qt5" -DCMAKE_BUILD_TYPE=Release . && cmake --build ..', shell=True)
        # os.system(f'"{self.depend_paths["vs_community"]}" && ')
        print("\ndone.\n")

        print("Building solution directory structure...")
        if not os.path.exists("abs-dist-win"): 
            os.mkdir("abs-dist-win")
        else:
            # otherwise, clean the directory
            shutil.rmtree("abs-dist-win")
            os.mkdir("abs-dist-win")

        # OK
        print("Copying .\\stremio.exe -> abs-dist-win\\stremio.exe...")
        shutil.copyfile('stremio.exe', 'abs-dist-win\\stremio.exe')
        print("\ndone.\n")
        
        # OK
        print("Copying C:\\Windows\\System32\\msvcr120.dll -> abs-dist-win\\msvcr120.dll...")
        shutil.copyfile('C:\\Windows\\System32\\msvcr120.dll', 'abs-dist-win\\msvcr120.dll')
        print("\ndone.\n")
        
        # ..\abs\stremio-depends\MPV\libmpv-2.dll
        # input(self.depend_paths['mpv'] + " : " + os.getcwd())
        print(f"Copying ..\\{self.depend_paths['mpv']} -> abs-dist-win\\{self.depend_paths['mpv']}...")
        shutil.copyfile(f"..\\{self.depend_paths['mpv']}", f'abs-dist-win\\' + self.depend_paths["mpv"].split("\\")[-1].replace("2", "1").replace("lib", ""))
        print("\ndone.\n")
        
        print("Copying .\\windows\\DS\\* -> abs-dist-win\\DS\\*...")
        shutil.copytree('windows\\DS', 'abs-dist-win\\DS')
        print("\ndone.\n")
        
        print("Copying server.js -> abs-dist-win\\server.js...")
        shutil.copyfile('server.js', 'abs-dist-win\\server.js')
        print("\ndone.\n")
        
        print(f"Copying .\\{self.depend_paths['openssl'].replace('openssl.exe', 'libcrypto-1_1.dll')} -> abs-dist-win\\libcrypto-1_1.dll...")
        shutil.copyfile(f"{self.depend_paths['openssl'].replace('openssl.exe', 'libcrypto-1_1.dll')}", 'abs-dist-win\\libcrypto-1_1.dll')
        print("\ndone.\n")
        
        print(f"Copying {self.where_is_path_var('node')} -> abs-dist-win\\node.exe...")
        shutil.copyfile(f"{self.where_is_path_var('node')}", 'abs-dist-win\\node.exe')
        print("\ndone.\n")
        
        print(f"Copying ..\\{self.depend_paths['ffmpeg']} -> abs-dist-win\\ffmpeg.exe...")
        shutil.copyfile(f"..\\{self.depend_paths['ffmpeg']}", 'abs-dist-win\\ffmpeg.exe')
        print("\ndone.\n")
        
        print("Deploying QT Dependencies...")
        os.system(f"{self.depend_paths['qt']} --qmldir . abs-dist-win\\stremio.exe")
        print("\ndone.\n")

        print("Build complete! You can find the build in the stremio-shell\\abs-dist-win directory.")