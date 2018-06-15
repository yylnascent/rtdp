import logging
import logging.handlers
import os
import sys

log = logging.getLogger()

def makedir(path):
    if os.path.exists(path):
        return

    try:
        os.makedirs(path)
    except OSError as exception:  # Python >2.5
        if exception.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            sys.stderr.write("create log_path failed: {}".format(path))

def __init_day_rotate_logging(log_path, logname=None, log_level=logging.INFO, when="MIDNIGHT", backup_count=7):
    """
    init day rotate logging
    @return:
    """
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
    __init_day_rotate_logging('.', logname, log_level)

def init_modules():
    """Initializes plugins."""
    log.debug("Importing modules...")

    # Import all realtime_intrusion modules.
    import modules.realtime_intrusion
    import_package(modules.realtime_intrusion)

    for category, entries in list_plugins().items():
        log.debug("Imported \"%s\" modules:", category)

        for entry in entries:
            if entry == entries[-1]:
                log.debug("\t `-- %s", entry.__name__)
            else:
                log.debug("\t |-- %s", entry.__name__)