import logging

"""
    Log a message to the specified log file
"""
def log(message, level):
    logger = logging.getLogger('root')
    hdlr = logging.FileHandler('/var/log/py.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)

    if level == "info":
        logger.info(message)
    elif level == "error":
        logger.error(message)

    hdlr.close()
    logger.removeHandler(hdlr)

    hdlr.close()

"""
    Log an informational message to the log file
"""
def info(message):
    log(message, "info")

"""
    Log an error message to the log file
"""
def error(message):
    log(message, "error")
        