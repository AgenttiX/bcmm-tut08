# Alpi Tolvanen 2017, Licence GPLv3+
import logging
import sys


#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def set_level(LEVEL):
    """
    Sets level of for error logging. Messages are printed from LEVEL and above.
    
    LEVEL       num. value
    --------------
    CRITICAL    50
    ERROR       40
    WARNING     30
    INFO        20
    DEBUG       10
    NOTSET      0
    
    Arguments:
        LEVEL     string or int
    """
    
    log_level = logging.NOTSET
    if isinstance(LEVEL, str):
        if LEVEL=="NOTSET":
            log_level = logging.NOTSET
        elif LEVEL=="INFO":
            log_level = logging.INFO
        elif LEVEL=="DEBUG":
            log_level = logging.DEBUG
        elif LEVEL=="WARNING":
            log_level = logging.WARNING
        elif LEVEL=="ERROR":
            log_level = logging.ERROR
        elif LEVEL=="CRITICAL":
            log_level = logging.CRITICAL
        else:
            raise RuntimeError("Unkown logging level")
    else:
        log_level = LEVEL

    logging.basicConfig(stream=sys.stderr, level=log_level, format='%(levelname)s - %(message)s')


def debug(*args):
    logging.debug(', '.join(map(str,args)))
    
def info(*args):
    logging.info(', '.join(map(str,args)))
    
def warning(*args):
    logging.warning(', '.join(map(str,args)))
    
def error(*args):
    logging.error(', '.join(map(str,args)))
