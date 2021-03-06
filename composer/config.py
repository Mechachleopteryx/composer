import csv
import os

from .errors import ConfigError

try:  # py3
    import configparser
except ImportError:  # py2
    import ConfigParser as configparser

# global config
CONFIG_FILENAME = "config.ini"
# wiki-specific config overrides
WIKI_CONFIG_FILENAME = CONFIG_FILENAME

LOGFILE_CHECKING = {"STRICT": 1, "LAX": 2}

DEFAULT_SCHEDULE = "standard"
DEFAULT_BULLET_CHARACTER = "*"


def _read_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def read_user_preferences(config_path):
    """Read composer config including wiki paths.

    :param str config_path: The location of the config file
    :returns dict: A dictionary corresponding to the user's preferences
        as indicated in the config file.
    """
    if not os.path.isfile(config_path):
        raise ConfigError(
            "Composer config file at {path} missing!".format(path=config_path)
        )
    config = _read_config(config_path)
    preferences = dict(config["general"])
    # convert from string to list
    preferences["wikis"] = next(csv.reader([preferences["wikis"]]))
    preferences["lessons_files"] = next(
        csv.reader([preferences["lessons_files"]])
    )
    return preferences


def update_wiki_specific_preferences(wikidir, preferences):
    """Read wiki-specific config, if present.

    This mutates the preferences dictionary, overriding any default config
    read previously where there is overlap.

    :param str wikidir: The location of the wiki
    :param dict preferences: Preferences read from the main config file
        that we will override here with wiki-specific config
    """
    config_path = os.path.join(wikidir, WIKI_CONFIG_FILENAME)
    if not os.path.isfile(config_path):
        return
    config = _read_config(config_path)
    wiki_preferences = dict(config["general"])
    # convert from string to list
    if wiki_preferences.get('lessons_files'):
        wiki_preferences["lessons_files"] = next(
            csv.reader([preferences["lessons_files"]])
        )
    # override lessons files, schedule, preferred bullet char, and
    # anything else
    preferences.update(wiki_preferences)
