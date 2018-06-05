import configparser
import os
import logging
import re

from lib.common.exceptions import RTDPConfigurationError
from lib.common.objects import Dictionary

from lib.common.constants import RTDP_ROOT

log = logging.getLogger(__name__)


class Config(object):
    """Configuration file parser."""

    def __init__(self, file_name="dataprocess"):
        """
        @param file_name: file name without extension.
        """

        config = configparser.ConfigParser()
        config.read(os.path.join(RTDP_ROOT, "conf", "%s.conf" % file_name))

        for section in config.sections():
            setattr(self, section, Dictionary())
            for name, raw_value in config.items(section):
                try:
                    # Ugly fix to avoid '0' and '1' to be parsed as a
                    # boolean value.
                    # We raise an exception to goto fail^w parse it
                    # as integer.
                    if config.get(section, name) in ["0", "1"]:
                        raise ValueError

                    value = config.getboolean(section, name)
                except ValueError:
                    try:
                        value = config.getint(section, name)
                    except ValueError:
                        value = config.get(section, name)

                setattr(getattr(self, section), name, value)

    def get(self, section):
        """Get option.
        @param section: section to fetch.
        @raise RTDPConfigurationError: if section not found.
        @return: option value.
        """
        try:
            return getattr(self, section)
        except AttributeError as e:
            raise RTDPConfigurationError("Option %s is not found in "
                                         "configuration, error: %s" %
                                         (section, e))