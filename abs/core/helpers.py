# Title:    Stremio Windows Build Script
# Author:   ShoobyDoo
# Date:     2023-03-13
# Edited:   2023-03-18
# Version:  0.1.0

import os
import re
import subprocess
import zipfile
import requests
import py7zr

from tqdm import tqdm


class Helpers:

    @staticmethod
    def cls() -> None:
        """
        Clears the console screen.
        """
        os.system('cls' if os.name == 'nt' else 'clear')


    @staticmethod
    def yes_no_prompt(prompt: str) -> bool:
        """
        Prompts the user for a yes or no answer given a prompt.

        Args:
            prompt (str): The prompt to display to the user.
        Returns:
            bool: True if the user answered yes, False if the user answered no.
        """
        yes = ["yes", "y"]
        no = ["no", "n"]

        while True:
            answer = input(f"{prompt}\nYes/No: ").lower()
            if answer in yes:
                return True
            elif answer in no:
                return False
    
    ynp = yes_no_prompt


    @staticmethod
    def download_file(url, out_filename: str, is_archive = True, out_path: str = '.\\abs\\stremio-depends\\'):
        """
        Downloads a file from a given url.

        Args:
            url (str): The url to download the file from.
            out_filename (str): The filename to save the file as.
        """

        #headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        if not os.path.exists(out_path): os.makedirs(out_path)

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            
            try:
                if ".zip" in r.headers['Content-Type'] or ".zip" in r.request.url:
                    out_filename = out_filename.replace(".exe", ".zip")
                elif ".7z" in r.headers['Content-Type'] or ".7z" in r.request.url:
                    out_filename = out_filename.replace(".exe", ".7z")
                else:
                    is_archive = False

            except KeyError as e:
                print(f"(!) {e} not found in headers... Assuming file is not an archive.")

            with open(f"{out_path}{out_filename}", 'wb') as f:
                pbar = tqdm(
                    unit_scale=True, 
                    total=int(r.headers['Content-Length']), 
                    desc=f"Downloading {out_filename}",
                    colour="green"
                )
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        pbar.update(len(chunk))

                pbar.close()
                print(f"Download of {out_filename} complete.\n")
        
        # now install it. method will handle archives as well.
        return (out_filename, is_archive)
    

    @staticmethod
    def basic_download(url, out_filename: str, out_path: str = ''):
        """
        Downloads a file from a given url.

        Args:
            url (str): The url to download the file from.
            out_filename (str): The filename to save the file as.
        """
        
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(f"{out_path}{out_filename}", 'wb') as f:
                pbar = tqdm(
                    unit_scale=True, 
                    total=int(r.headers['Content-Length']), 
                    desc=f"Downloading {out_filename}",
                    colour="green"
                )
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

                pbar.close()


    @staticmethod
    def get_filename_from_cd(cd):
        """
        Get filename from content-disposition
        """
        if not cd:
            return None
        fname = re.findall('filename=(.+)', cd)
        if len(fname) == 0:
            return None
        return fname[0]


    @staticmethod
    def install_file(filename: str, is_archive: bool, out_path: str = 'abs\\stremio-depends\\') -> str:
        """
        Installs a file.

        Args:
            filename (str): The filename to install.
        """

        if is_archive:
            print("Installation is archive. Extracting...")

            if filename.endswith(".7z"):
                out_folder = f"{out_path}{filename.replace('.7z', '')}"

                with py7zr.SevenZipFile(f"{out_path}{filename}", 'r') as zip_ref:
                    zip_ref.extractall(f"{out_path}{filename.replace('.7z', '')}")
                    
            else:
                out_folder = f"{out_path}{filename.replace('.zip', '')}"

                with zipfile.ZipFile(f"{out_path}{filename}", 'r') as zip_ref:
                    zip_ref.extractall(f"{out_path}{filename.replace('.zip', '')}")
            
            print(f"Cleaning up...")
            os.remove(f"{out_path}{filename}")

            if out_folder == 'abs\\stremio-depends\\FFMpeg':
                return f"""abs\\stremio-depends\\FFMpeg\\{os.listdir(f"abs/stremio-depends/{filename.replace('.zip', '')}")[0]}\\bin\\ffmpeg.exe"""
            elif out_folder == 'abs\\stremio-depends\\MPV':
                return f"{out_folder}\\libmpv-2.dll" # IDK if this will work, but it's worth a shot.

        else:
            print(f"Installing {filename}... Please see and complete installation in open window.")
            subprocess.run([f"{out_path}{filename}"])
            if filename == "VS_Community.exe": input("The visual studio installer will now start. Ensure that you also select \"Desktop C++\" during the installation. (Roughly ~4.5gb)\nThis inconvenience is only present on the first run of this script, assuming you do not have visual studio installed.\n\nPress [ENTER] once installation is complete to continue...")
        
        print(f"Installation of {filename} complete.\n")
