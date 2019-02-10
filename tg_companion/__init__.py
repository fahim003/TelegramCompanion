from argparse import ArgumentParser
from distutils.util import strtobool as sb
import socks
import sys
import os
import logging
import dotenv


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)


if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    )
    quit(1)

parser = ArgumentParser()
parser.add_argument(
    "--config", help="Display all the config variables", action="store_true"
)

parser.add_argument("--install", help="Install any given plugin. Usage: --install <pluginname> or <user/repo/plugin_name>.")

CONFIG_VALUES = [
    "APP_ID            : (required) Your telegram app id from https://my.telegram.org/apps",
    "APP_HASH          : (required) Your telegram app hash from https://my.telegram.org/apps",
    "DB_URI            : (required) Your postgress database url. Leave empty to disable the modules that use it",
    "DEBUG             : (optional) Set True if you want to generate log files from exceptions",
    "STATS_TIMER       : (optional) Update stats every x seconds. Default = 3600 seconds. Set to 0 to disable"
                            "WARNING: If enabled the companion will not respond to your commands for 5 seconds when starting the bot for the first time",
    "BLOCK_PM          : (optional) Set to True if you want to block new PMs. New PMs will be deleted and user blocked",
    "NOPM_SPAM         : (optional) Set to True if you want to block users that are spamming your PMs.",
    "SUBPROCESS_ANIM   : (optional) Set to True if you want to enable animations when using a terminal command."
                            "WARNING: When executing commands with long outputs it might trigger a flood wait that will restrict you from editing any send messages for a given time. Usualy just 250 seconds."
    "PROXY_TYPE        : (optional) Your proxy type HTTP/SOCKS4/SOCKS5. Leave empty to disable proxy.",
    "HOST              : (optional) The host of the used proxy.",
    "PORT              : (optional) The port of the used proxy.",
    "USERNAME          : (optional) The username of the used proxy. (If any)",
    "PASSWORD          : (optional) The password of the used proxy. (If any)",
    "SESSION_NAME      : (optional) Custom session name. Leave empty to use the default session name",
    "ENABLE_SSH        : (optional) Set True if you want to execute/upload from a ssh server",
    "SSH_HOSTNAME      : (optional) The hostname or address to connect to.",
    "SSH_PORT          : (optional) The hostname or address to connect to.",
    "SSH_USERNAME      : (optional) Username to authenticate as on the server.",
    "SSH_PASSWORD      : (optional) The password to use for client password authentication",
    "SSH_PASSPHRASE    : (optional) The passphrase for your ssh connection.",
    "SSH_KEY           : (optional) The private key which will be used to authenticate this client",
]

args = parser.parse_args()

TO_INSTALL = ""
if args.config:
    print("\n".join(CONFIG_VALUES))
    quit(1)

if args.install:
    TO_INSTALL = args.install


dotenv.load_dotenv("config.env")

APP_ID = os.environ.get("APP_ID", None)
APP_HASH = os.environ.get("APP_HASH", None)
SESSION_NAME = os.environ.get("SESSION_NAME", "tg_companion")
DB_URI = os.environ.get("DB_URI", None)
DEBUG = sb(os.environ.get("DEBUG", "False"))

PROXY_TYPE = os.environ.get("PROXY_TYPE", None)
HOST = os.environ.get("HOST", None)
PORT = os.environ.get("PORT", None)
USERNAME = os.environ.get("USERNAME", None)
PASSWORD = os.environ.get("PASSWORD", None)

BLOCK_PM = sb(os.environ.get("BLOCK_PM", "False"))
NOPM_SPAM = sb(os.environ.get("NOPM_SPAM", "False"))
STATS_TIMER = int(os.environ.get("STATS_TIMER", 3600))
SUBPROCESS_ANIM = sb(os.environ.get("SUBPROCESS_ANIM", "False"))

ENABLE_SSH = sb(os.environ.get('ENABLE_SSH', "False"))
SSH_HOSTNAME = os.environ.get('SSH_HOSTNAME', '::1')
SSH_PORT = os.environ.get('SSH_PORT', 22)
SSH_USERNAME = os.environ.get('SSH_USERNAME', None)
SSH_PASSWORD = os.environ.get('SSH_PASSWORD', None)
SSH_PASSPHRASE = os.environ.get('SSH_PASSPHRASE', None)
SSH_KEY = os.environ.get('SSH_KEY', None)

TRAVIS = os.environ.get("TEST_BUILD", False)

proxy = None
proxy_type = None
proxy_addr = HOST
proxy_port = PORT
proxy_username = USERNAME
proxy_password = PASSWORD
if PROXY_TYPE:
    if PROXY_TYPE == "HTTP":
        proxy_type = socks.HTTP
    elif PROXY_TYPE == "SOCKS4":
        proxy_type = socks.SOCKS4
    elif PROXY_TYPE == "SOCKS5":
        proxy_type = socks.SOCKS5
    else:
        proxy_type = None

    proxy = (proxy_type, proxy_addr, int(proxy_port), False)
if USERNAME and PASSWORD:
    proxy = (
        proxy_type,
        proxy_addr,
        proxy_port,
        False,
        proxy_username,
        proxy_password)
