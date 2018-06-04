# Copyright (C) 2012-2013 Claudio Guarnieri.
# Copyright (C) 2014-2018 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import ConfigParser
import click
import os
import logging
import re

from lib.common.exceptions import RTDPConfigurationError
from lib.common.objects import Dictionary

log = logging.getLogger(__name__)


class Config(object):
    """Configuration file parser."""

    def __init__(self, file_name="dataprocess"):
        """
        @param file_name: file name without extension.
        """

        self.sections = {}

        try:
            config.read(os.path.join('..', '..', 'conf', '%s.conf' % file_name))
        except ConfigParser.ParsingError as e:
            raise CuckooConfigurationError(
                "There was an error reading in the $CWD/conf/%s.conf "
                "configuration file. Most likely there are leading "
                "whitespaces in front of one of the key=value lines defined. "
                "More information from the original exception: %s" %
                (file_name, e)
            )

        if file_name not in self.configuration:
            log.error("Unknown config file %s.conf", file_name)
            return

        for section in config.sections():

            self.sections[section] = Dictionary()
            setattr(self, section, self.sections[section])

            try:
                items = config.items(section)
            except ConfigParser.InterpolationMissingOptionError as e:
                log.error("Missing environment variable(s): %s", e)
                raise CuckooConfigurationError(
                    "Missing environment variable: %s" % e
                )
            except ValueError as e:
                if e.message == "incomplete format key":
                    raise CuckooConfigurationError(
                        "One of the fields that you've filled out in "
                        "$CWD/conf/%s contains the sequence '%(' which is "
                        "interpreted as environment variable sequence, e.g., "
                        "'%(PGPASSWORD)s' would locate a PostgreSQL "
                        "password. Please update the field to correctly "
                        "state the environment variable or change it in a "
                        "way that '%(' is no longer in the variable."
                    )
                raise

            for name, raw_value in items:
                if name in self.env_keys:
                    continue

                if "\n" in raw_value:
                    wrong_key = "???"
                    try:
                        wrong_key = raw_value.split("\n", 1)[1].split()[0]
                    except:
                        pass

                    raise CuckooConfigurationError(
                        "There was an error reading in the $CWD/conf/%s.conf "
                        "configuration file. Namely, there are one or more "
                        "leading whitespaces before the definition of the "
                        "'%s' key/value pair in the '%s' section. Please "
                        "remove those leading whitespaces as Python's default "
                        "configuration parser is unable to handle those "
                        "properly." % (file_name, wrong_key, section)
                    )

                if not raw and name in types:
                    # TODO Is this the area where we should be checking the
                    # configuration values?
                    # if not types[name].check(raw_value):
                    #     print file_name, section, name, raw_value
                    #     raise

                    value = types[name].parse(raw_value)
                else:
                    if not loose:
                        log.error(
                            "Type of config parameter %s:%s:%s not found! "
                            "This may indicate that you've incorrectly filled "
                            "out the Cuckoo configuration, please double "
                            "check it.", file_name, section, name
                        )
                    value = raw_value

                self.sections[section][name] = value

    def get(self, section):
        """Get option.
        @param section: section to fetch.
        @raise CuckooConfigurationError: if section not found.
        @return: option value.
        """
        if section not in self.sections:
            raise CuckooConfigurationError(
                "Option %s is not found in configuration" % section
            )

        return self.sections[section]

def parse_options(options):
    """Parse the analysis options field to a dictionary."""
    ret = {}
    for field in options.split(","):
        if "=" not in field:
            continue

        key, value = field.split("=", 1)
        ret[key.strip()] = value.strip()
    return ret

def emit_options(options):
    """Emit the analysis options from a dictionary to a string."""
    return ",".join("%s=%s" % (k, v) for k, v in sorted(options.items()))

def config(s, cfg=None, strict=False, raw=False, loose=False, check=False):
    """Fetch a configuration value, denoted as file:section:key."""
    if s.count(":") != 2:
        raise RuntimeError("Invalid configuration entry: %s" % s)

    file_name, section, key = s.split(":")

    if check:
        strict = raw = loose = True

    type_ = Config.configuration.get(file_name, {}).get(section, {}).get(key)
    if strict and type_ is None:
        raise CuckooConfigurationError(
            "No such configuration value exists: %s" % s
        )

    required = type_ is not None and type_.required
    index = file_name, cfg, cwd(), strict, raw, loose

    if index not in _cache:
        _cache[index] = Config(
            file_name, cfg=cfg, strict=strict, raw=raw, loose=loose
        )

    config = _cache[index]

    if strict and required and section not in config.sections:
        raise CuckooConfigurationError(
            "Configuration value %s not present! This may indicate that "
            "you've incorrectly filled out the Cuckoo configuration, "
            "please double check it." % s
        )

    section = config.sections.get(section, {})
    if strict and required and key not in section:
        raise CuckooConfigurationError(
            "Configuration value %s not present! This may indicate that "
            "you've incorrectly filled out the Cuckoo configuration, "
            "please double check it." % s
        )

    value = section.get(key, type_.default if type_ else None)

    if check and not type_.check(value):
        raise CuckooConfigurationError(
            "The configuration value %r found for %s is invalid. Please "
            "update your configuration!" % (value, s)
        )

    return value
