import logging


class FaviconFilter(logging.Filter):
    def filter(self, record):
        return not '/favicon.ico HTTP' in record.getMessage()

# logger.addFilter(NoParsingFilter())
