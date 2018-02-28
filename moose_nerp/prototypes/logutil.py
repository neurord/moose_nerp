import inspect
import logging

class Message(object):
    def __init__(self, fmt, args):
        self.fmt = fmt
        self.args = args

    def __str__(self):
        return self.fmt.format(*self.args)

class StyleAdapter(logging.LoggerAdapter):
    def __init__(self, logger, extra=None):
        super(StyleAdapter, self).__init__(logger, extra or {})

    def log(self, level, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self.logger._log(level, Message(msg, args), (), **kwargs)

    def debug(self, *args, **kwargs):
        return self.log(logging.DEBUG, *args, **kwargs)
    def info(self, *args, **kwargs):
        return self.log(logging.INFO, *args, **kwargs)
    def warning(self, *args, **kwargs):
        return self.log(logging.WARNING, *args, **kwargs)
    def error(self, *args, **kwargs):
        return self.log(logging.ERROR, *args, **kwargs)

def Logger(name=None):
    if name is None:
        frame = inspect.stack()[1]
        mod = inspect.getmodule(frame[0])
        if mod is not None:
            name = mod.__name__
        else:
            name = '__main__'
    FORMAT = '%(process)d - %(filename)s - %(lineno)d - %(funcName)s - %(levelname)s - %(message)s' #SRIRAM 02152018
    logging.basicConfig(format=FORMAT)
    return StyleAdapter(logging.getLogger(name))
