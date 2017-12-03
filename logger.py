import logging
import sys

"""
This module works as a wrapper around logging module.



Usage:

main.py:
    # Notice that in root-logger works as a level-bottleneck for all other module-loggers
    import logger; 
    log = logger.getLogger(__name__, level="NOTSET", disabled=False) # Root logger


otherModule.py:
    # Modules-loggers can be controlled individiually
    import logger;
    log = logger.getLogger(__name__, level="INFO", disabled=False, colors=True)
    ...
    log.debug("A Debug message")



These are levels possible levels
    LEVEL       numerical value
    --------------
    CRITICAL    50
    ERROR       40
    WARNING     30
    INFO        20
    DEBUG       10
    NOTSET      0
"""


class _Logger:
    def __init__(self, name):
        self._logger = logging.getLogger(name)
        
    def getActualLogger(self):
        return self._logger
    
    def debug(self, *args):
        self._logger.debug(', '.join(map(str,args)))
    
    def info(self, *args):
        self._logger.info(', '.join(map(str,args)))
        
    def warning(self, *args):
        self._logger.warning(', '.join(map(str,args)))
        
    def error(self, *args):
        self._logger.error(', '.join(map(str,args)))
    
    def critical(self, *args):
        self._logger.critical(', '.join(map(str,args)))
        
    def setLevel(self, LEVEL, colors=False):
        """
        Sets level of for error logging. Messages are printed from LEVEL and above.
        
        Arguments:
            LEVEL     string or int
        """
        
        log_level = logging.NOTSET
        if isinstance(LEVEL, str):
            if LEVEL=="NOTSET":
                # Notice normally NOTSET is level 0 except for root 30
                log_level = logging.NOTSET
            elif LEVEL=="DEBUG":
                log_level = logging.DEBUG
            elif LEVEL=="INFO":
                log_level = logging.INFO
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
        
        self._logger.setLevel(log_level) 
        
        if colors == True:
            OKBLUE = '\033[94m'
            OKGREEN = '\033[92m'
            WARNING = '\033[93m'
            ENDC = '\033[0m'
            form_str = OKBLUE + '%(name)s %(levelname)s:' + ENDC + ' %(message)s'
        else:
            form_str = '%(name)s %(levelname)s: %(message)s'
        
        formatter = logging.Formatter(form_str)
        consoleHandler = logging.StreamHandler()
        
        consoleHandler.setLevel(log_level) # How does this differ from logger.setLevel()?
        consoleHandler.setFormatter(formatter)
        
        self._logger.addHandler(consoleHandler)


def getLogger(name, level="DEBUG", disabled=False, colors=False):
    log = _Logger(name)
    log.setLevel(level, colors=colors)
    log.getActualLogger().disabled = disabled

    return log
