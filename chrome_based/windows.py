import logging
import base64
import getpass
import json
import os
from pathlib import Path
from typing import Union

import win32crypt

from chrome_based.base import ChromeBase
from exceptions import Exit


class ChromeWindows(ChromeBase):
    def __init__(self, browser: str = "chrome", verbose: bool = False):
        """ Decryption class for Windows 10.
        Notice that older versions of Windows haven't been tried yet.
        The code will probably not work as expected.
        :param browser: Choose which browser use. Available: "chrome" (default), "opera", and "brave".
        :param verbose: print output
        """

        super(ChromeWindows, self).__init__(verbose)

        assert browser in self.available_browsers, Exit(Exit.BROWSER_NOT_IMPLEMENTED)

        self.username = getpass.getuser()
        self.browser = browser.lower()

        self._browser_paths = []
        self._database_paths = []
        self.keys = []

        base_path = r"C:\Users\{}\AppData".format(getpass.getuser())

        self.browsers_paths = {
            "chrome": os.path.join(base_path, r"Local\Google\{chrome}\User Data"),
            "opera": os.path.join(base_path, r"Roaming\Opera Software\Opera Stable\Local State"),
            "brave": os.path.join(base_path, r"Local\BraveSoftware\Brave-Browser\User Data\Local State")
        }

        self.browsers_database_paths = {
            "chrome": os.path.join(base_path, r"Local\Google\{chrome}\User Data"),
            "opera": os.path.join(base_path, r"Roaming\Opera Software\Opera Stable\Login Data"),
            "brave": os.path.join(base_path, r"Local\BraveSoftware\Brave-Browser\User Data\Default\Login Data")
        }

    def get_windows(self):
        """Return database paths and keys for Windows
        """

        if self.browser == "chrome":
            chrome_versions = ['chrome', 'chrome dev', 'chrome beta', 'chrome canary']

            # Fetch all Chrome versions paths
            self._browser_paths = [
                os.path.join(self.browsers_paths["chrome"].format(chrome=ver), "Local State")
                for ver in chrome_versions if
                os.path.exists(self.browsers_paths["chrome"].format(chrome=ver))]

            # Fetch all database paths
            self._database_paths = [
                os.path.join(self.browsers_paths["chrome"].format(chrome=ver), r"default\Login Data")
                for ver in chrome_versions if
                os.path.exists(self.browsers_paths["chrome"].format(chrome=ver))]

        else:
            self._browser_paths = [self.browsers_paths[self.browser]]
            self._database_paths = [self.browsers_database_paths[self.browser]]

        # Get the AES key
        self.keys = [self.__class__.get_encryption_key(path) for path in self.browser_paths]
        return self.database_paths, self.keys

    @property
    def browser_paths(self):
        return self._browser_paths

    @property
    def database_paths(self):
        return self._database_paths

    @staticmethod
    def get_encryption_key(path: Union[Path, str]):
        """Return the encryptation key of a path
        """

        try:
            with open(path, "r", encoding="utf-8") as file:  # Open the "Local State" file
                local_state = file.read()
                local_state = json.loads(local_state)

        except FileNotFoundError:
            logging.error(f"Code {Exit.FILE_NOT_FOUND}")
            raise Exit(Exit.FILE_NOT_FOUND)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]  # Remove "DPAPI" string at the beginning
        # Return the decrypted key that was originally encrypted
        # using a session key derived from current user's login credentials
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
