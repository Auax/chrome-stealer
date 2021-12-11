import logging

# Setup
# Need to import this to the main file
# Add logging.StreamHandler() to print to console
handlers = [logging.FileHandler('app.log')]
logging.basicConfig(
    format="%(asctime)s - %(levelname)s : %(message)s",
    level=logging.INFO,
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=handlers)
