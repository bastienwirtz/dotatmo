import logging
import logging.handlers
import settings

logger = logging.getLogger('Dotatmo')
logger.setLevel(logging.INFO)
log_format = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')


# File logging configuration
handler = logging.handlers.SysLogHandler(address = '/dev/log')
handler.setFormatter(log_format)
logger.addHandler(handler)

# DEBUG logging
if settings.DEBUG:
    console = logging.StreamHandler()
    console.setFormatter(log_format)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)
