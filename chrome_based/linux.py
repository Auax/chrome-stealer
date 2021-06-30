import os

import secretstorage
from Crypto.Protocol import KDF

from chrome_based.base import ChromeBase
from exceptions import Exit
from logger import logger


class ChromeLinux(ChromeBase):
    """ Decryption class for Chrome in Linux OS """

    def __init__(self, browser: str = "chrome", verbose: bool = False):
        """ Decryption class for Windows 10.
        Notice that older versions of Windows haven't been tried yet.
        The code will probably not work as expected.
        :param browser: Choose which browser use. Available: "chrome" (default), "opera", and "brave".
        :param verbose: print output
        """

        super(ChromeLinux, self).__init__(verbose)

        assert browser in self.available_browsers, Exit(Exit.BROWSER_NOT_IMPLEMENTED)

        self.key = []
        self.browser = browser
        base_path = os.getenv('HOME')

        self.browsers_paths = {
            "chrome": base_path + "/.config/google-chrome/Default/",
            "opera": base_path + "/.config/opera/",
            "brave": base_path + "/.config/BraveSoftware/Brave-Browser/Default"
        }

        if not os.path.isdir(self.browsers_paths[self.browser]):
            logger.error(f"Code {Exit.BROWSER_NOT_FOUND}")
            raise Exit(Exit.BROWSER_NOT_FOUND)

        self.browsers_database_paths = {
            "chrome": base_path + "/.config/google-chrome/Default/Login Data",
            "opera": base_path + "/.config/opera/Login Data",
            "brave": base_path + "/.config/BraveSoftware/Brave-Browser/Default/Login Data"
        }

    def get_linux(self):
        """Return database paths and keys for Linux
        """
        passw = 'peanuts'.encode('utf8')  # Set default
        bus = secretstorage.dbus_init()  # New connection to session bus
        collection = secretstorage.get_default_collection(bus)
        for item in collection.get_all_items():  # Iterate
            if item.get_label() == 'Chrome Safe Storage':
                passw = item.get_secret()  # Retrieve item
                break

        self.key = KDF.PBKDF2(passw, b'saltysalt', 16, 1)
        return [self.browsers_database_paths[self.browser]], [self.key]

    @property
    def database_paths(self):
        # Return all database paths
        return [self._database_paths]
