import asyncio
import inspect
import os
import io
import sys
import zipfile
from datetime import datetime

from alchemysession import AlchemySessionContainer
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpcerrorlist import PhoneCodeInvalidError

from tg_companion import APP_HASH, APP_ID, DB_URI, DEBUG, SESSION_NAME, LOGGER, proxy
from tg_companion._version import __version__
from getpass import getpass


loop = asyncio.get_event_loop()


class CompanionClient(TelegramClient):

    def __init__(self, session_name, app_id, app_hash):
        LOGGER.info("Starting TelegramCompanion")
        super().__init__(
            session_name,
            app_id,
            app_hash,
            proxy=proxy,
            app_version=__version__.public())

        ("Connecting to Telegram")

        try:
            loop.run_until_complete(self.connect())
        except ConnectionError:
            LOGGER.info("Failed to connect to Telegram Server.. Retrying")
            loop.run_until_complete(self.connect())

        if not loop.run_until_complete(self.is_user_authorized()):
            LOGGER.info("Welcome to Telegram CompanionCompanion.. \n\n")
            phone = input("Enter your phone: ")
            loop.run_until_complete(self.sign_in(phone))

            self_user = None
            while self_user is None:

                code = input(
                    "Please enter the code you just recieved.. Press enter to send the code via SMS: ")

                if not code:
                    loop.run_until_complete(
                        self.send_code_request(
                            phone, force_sms=True))
                    code = input(
                        "Please Enter the code you just recieved: ")
                try:
                    self_user = loop.run_until_complete(
                        self.sign_in(code=code))
                except Exception as exc:
                    if isinstance(exc, PhoneCodeInvalidError):
                        code = input("The phone code entered was invalid. Try again: ")
                    elif isinstance(exc, SessionPasswordNeededError):
                        password = getpass(
                            "Two step verification is enabled. Please enter your password: ")

                        self_user = loop.run_until_complete(
                            self.sign_in(password=password))

        LOGGER.info("Connected!!")

    async def send_from_disk(self, event, path, caption=None, force_document=False, use_cache=None, reply_to=None):
        if os.path.isfile(path):
            f_name = os.path.basename(path)
            f_size, unit = self.convert_file_size(os.path.getsize(f_name))
            await event.edit(
                f"**Uploading**:\n\n"
                f"  __File Name:__ `{f_name}`\n"
                f"  __Size__: `{f_size}` {unit}\n"
            )

            await self.send_file(event.chat_id, path, file_name=f_name,
                                 force_document=force_document, reply_to=reply_to, progress_callback=None)
            await event.delete()

        elif os.path.isdir(path):
            d_name = os.path.dirname(path)
            d_size = 0

            try:
                with io.BytesIO() as memzip:
                    with zipfile.ZipFile(memzip, mode="w") as zf:
                        await event.edit("Processing ZipFile from folder")
                        for file in os.listdir(path):
                            zf.write(f"{path}{file}")
                            d_size = d_size + os.path.getsize(f"{path}{file}")

                    memzip.name = f"{d_name}.zip"
                    memzip.seek(0)
                    d_size, unit = self.convert_file_size(d_size)
                    await event.edit(
                        f"**Uploading**:\n\n"
                        f"  __Folder Name:__ `{d_name}`\n"
                        f"  __Size__: `{d_size}` {unit}\n"
                    )

                    await client.send_file(event.chat_id, file=memzip, allow_cache=None, progress_callback=None)
                    await event.delete()
            except FileNotFoundError:
                await event.edit(f"`{path}` doesn't exist.")
                return
        else:
            await event.edit(f"{path} doesn't exist.")
            return

    def convert_file_size(self, size):
        power = 2**10
        n = 0
        units = {
            0: '',
            1: 'kilobytes',
            2: 'megabytes',
            3: 'gigabytes',
            4: 'terabytes'}
        while size > power:
            size /= power
            n += 1
        return round(size, 2), units[n]

    def on_timer(self, seconds):
        """
        A decorator that runs a decorated function every x seconds.

        Args:

        seconds (int): Updates the function every given second
        """
        def decorator(fcn):
            async def wrapper():
                while not client.is_connected():
                    await asyncio.sleep(1)
                while True:
                    if int(seconds) == 0:
                        break
                    await fcn()
                    await asyncio.sleep(seconds)
            loop.create_task(wrapper())

            return wrapper
        return decorator

    def log_exception(self, func):

        async def wrapper(*args, **kwds):
            __lgw_marker_local__ = 0

            try:
                return await func(*args, **kwds)
            except Exception as e:

                exc_time = datetime.now().strftime("%m_%d_%H:%M:%S")

                file_name = f"{exc_time}_{type(e).__name__}_{func.__name__}"

                if not DEBUG:
                    raise

                if not os.path.exists('logs/'):
                    os.mkdir('logs/')

                with open(f"logs/{file_name}.log", "a") as log_file:
                    log_file.write(f"Exception thrown, {type(e)}: {str(e)}\n")
                    frames = inspect.getinnerframes(sys.exc_info()[2])
                    for frame_info in reversed(frames):
                        f_locals = frame_info[0].f_locals
                        if "__lgw_marker_local__" in f_locals:
                            continue

                        log_file.write(f"File{frame_info[1]},"
                                       f"line {frame_info[2]}"
                                       f" in {frame_info[3]}\n"
                                       f"{     frame_info[4][0]}\n")

                        for k, v in f_locals.items():
                            log_to_str = str(v).replace("\n", "\\n")
                            log_file.write(f"    {k} = {log_to_str}\n")
                    log_file.write("\n")

                raise

        return wrapper


container = AlchemySessionContainer(DB_URI)
session = container.new_session(SESSION_NAME)

client = CompanionClient(session, APP_ID, APP_HASH)
