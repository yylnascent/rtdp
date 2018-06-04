import logging

log = logging.getLogger()

def __init_day_rotate_logging(log_path, logname=None, log_level=logging.INFO, when="MIDNIGHT", backup_count=7):
    """
    init day rotate logging
    @return:
    """
    log = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s [%(name)s:%(lineno)d][%(thread)d] %(levelname)s: %(message)s")

    if logname and log_path:
        makedir(log_path)
        if os.path.isdir(log_path):
            filename = "%s.log" % logname
            filepath = os.path.join(log_path, filename)
            fh = logging.handlers.TimedRotatingFileHandler(filepath, when=when, backupCount=backup_count)
            fh.setFormatter(formatter)
            log.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    log.addHandler(sh)

    log.setLevel(log_level)

def init_logging(logname="scheduler", log_level=logging.INFO):
    """Initializes logging."""
    __init_day_rotate_logging('.')

    log.setLevel(log_level)
