import logging

"""
This module works as a wrapper around logging module.


Usage:

main.py:
    # Notice that in root-logger works as a level-bottleneck for all other module-loggers
    import logger; 
    log = logger.getLogger(__name__, level="NOTSET", disabled=False) # Root logger


otherModule.py:
    # Modules-loggers can be controlled individually
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
    
    # Todo implement progressbar-function (I already have made that, but its somewhere in my files)
"""


class _Logger:
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
        
    def get_actual_logger(self) -> logging.Logger:
        """
        Get the raw logger that this logging API uses
        :return: raw logger
        """
        return self._logger
    
    def debug(self, *args):
        self._logger.debug(', '.join(map(str, args)))
    
    def info(self, *args):
        self._logger.info(', '.join(map(str, args)))
        
    def warning(self, *args):
        self._logger.warning(', '.join(map(str, args)))

    def error(self, *args):
        self._logger.error(', '.join(map(str, args)))
    
    def critical(self, *args):
        self._logger.critical(', '.join(map(str, args)))

    def set_level(self, level, colors=False):
        """
        Sets level of for error logging. Messages are printed from LEVEL and above.
        :param level: string or int
        :param colors:
        :return: -
        """
        
        # log_level = logging.NOTSET
        if isinstance(level, str):
            if level == "NOTSET":
                # Notice normally NOTSET is level 0 except for root 30
                log_level = logging.NOTSET
            elif level == "DEBUG":
                log_level = logging.DEBUG
            elif level == "INFO":
                log_level = logging.INFO
            elif level == "WARNING":
                log_level = logging.WARNING
            elif level == "ERROR":
                log_level = logging.ERROR
            elif level == "CRITICAL":
                log_level = logging.CRITICAL
            else:
                raise RuntimeError("Unkown logging level")
        else:
            log_level = level
        
        self._logger.setLevel(log_level) 
        
        # if colors:
        #     pass
        
        def decorate_emit(fn):
            # https://stackoverflow.com/questions/20706338/color-logging-using-logging-module-in-python
            # add the methods we need to the class
            def new(*args):
                levelno = args[0].levelno
                lightgray = '\033[37m'
                ENDC = '\033[0m'
                
                if levelno >= logging.CRITICAL:
                    lvl = "CRITICAL"
                    color = '\033[91m\033[1m\033[4m'  #FAIL (red) BOLD UNDERLINE
                elif levelno >= logging.ERROR:
                    lvl = "ERROR"
                    color = '\033[91m'  #FAIL (red)
                elif levelno >= logging.WARNING:
                    lvl = "WARNING"
                    color = '\033[93m'  # WARNING (yellow)
                elif levelno >= logging.INFO:
                    lvl = "INFO"
                    color = '\033[92m'  # OKGREEN
                elif levelno >= logging.DEBUG:
                    lvl = "DEBUG"
                    color = '\033[94m'  # OKBLUE # these colors are from Bldender scripts
                else:
                    lvl = "NOTSET"
                    color = lightgray
                
                # add colored *** in the beginning of the message
                args[0].msg = color + lvl + ":" + ENDC + " " + str(args[0].msg)

                # new feature i like: bolder each args of message 
                args[0].args = tuple('\x1b[1m' + arg + '\x1b[0m' for arg in args[0].args)
                return fn(*args)
            return new

        console_handler = logging.StreamHandler()

        if colors:
            light_gray = '\033[37m'
            ENDC = '\033[0m'
            form_str = light_gray + '%(name)s' + ENDC + ' %(message)s'
            console_handler.emit = decorate_emit(console_handler.emit)
        else:
            form_str = '%(name)s %(levelname)s: %(message)s'
        
        formatter = logging.Formatter(form_str)
        
        console_handler.setLevel(log_level)  # How does this differ from logger.setLevel()?
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(console_handler)


def get_logger(name, level="DEBUG", disabled=False, colors=False):
    log = _Logger(name)
    log.set_level(level, colors=colors)
    log.get_actual_logger().disabled = disabled

    return log
