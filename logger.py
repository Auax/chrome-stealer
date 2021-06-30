import logging

# Create custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handler
f_handler = logging.FileHandler("logger.log")
f_handler.setLevel(logging.ERROR)

# Create formatter and add it to the handler
f_format = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s:%(funcName)s() - %(levelname)s: %(message)s')
f_handler.setFormatter(f_format)

# Add handler to the logger
logger.addHandler(f_handler)
