import io
import os
import platform
import re
import sys
import time
from html import escape

import aiohttp
import telethon
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import User

from tg_companion.modules.rextester.api import Rextester, UnknownLanguage
from tg_companion.tgclient import client

from .._version import __version__


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ping"))
@client.log_exception
async def ping(e):
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        await session.get("https://www.google.com")
    end_time = time.time()
    ping_time = float(end_time - start_time) * 1000
    await e.edit(f"Ping time was: {ping_time}ms")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.version"))
@client.log_exception
async def version(e):
    bot_version = __version__.public()
    python_version = platform.python_version()
    telethon_version = telethon.__version__

    await e.edit(f"__Bot Version__ = `{bot_version}`\n\n__Python Version__ = `{python_version}`\n\n__Telethon Version__ = {telethon_version}")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.info"))
@client.log_exception
async def user_info(e):
    message = e.message
    user = await e.get_sender()
    chat = await e.get_chat()

    if e.reply_to_msg_id:
        message = await e.get_reply_message()
        user = await message.get_sender()

    if len(e.text.split()) > 1:
        user = e.text.split()[1]
        try:
            user = await client.get_entity(user)
        except Exception as exc:
            await e.reply(str(exc))
            return

        if not isinstance(user, User):
            await e.reply(f"`@{user.username}` is not a User")
            return

    full_user = await client(GetFullUserRequest(user.id))
    firstName = full_user.user.first_name
    lastName = full_user.user.last_name
    username = full_user.user.username
    user_id = full_user.user.id
    common_chats = full_user.common_chats_count

    REPLY = "<b>User Info:</b>\n"

    REPLY += f"\nFirst Name: {escape(firstName)}"

    if lastName:
        REPLY += f"\nLast Name: {escape(lastName)}"
    if username:
        REPLY += f"\nUsername: @{escape(username)}"
    REPLY += f"\nPermanent user link: <a href=\"tg://user?id={user_id}\">link</a>"
    if full_user.about:
        REPLY += f"\n\n<b>About User:</b>\n{escape(full_user.about)}"
    if not full_user.user.is_self:
        REPLY += f"\n\nYou have <code>{escape(common_chats)}</code> chats in common with this user"

    await client.send_message(
        chat.id, REPLY, reply_to=message.id, link_preview=False, file=full_user.profile_photo, parse_mode="html"
    )


@client.on(events.NewMessage(outgoing=True, pattern=r"^\$"))
@client.log_exception
async def rextestercli(e):
    stdin = ""
    message = e.text
    chat = await e.get_chat()

    if len(message.split()) > 1:
        regex = re.search(
            r"^\$([\w.#+]+)\s+([\s\S]+?)(?:\s+\/stdin\s+([\s\S]+))?$",
            message,
            re.IGNORECASE,
        )
        language = regex.group(1)
        code = regex.group(2)
        stdin = regex.group(3)

        try:
            rextester = Rextester(language, code, stdin)
            res = await rextester.exec()
        except UnknownLanguage as exc:
            await e.edit(str(exc))
            return

        output = ""
        output += f"**Language:**\n```{language}```"
        output += f"\n\n**Source:** \n```{code}```"

        if res.result:
            output += f"\n\n**Result:** \n```{res.result}```"

        if res.warnings:
            output += f"\n\n**Warnings:** \n```{res.warnings}```\n"

        if res.errors:
            output += f"\n\n**Errors:** \n'```{res.errors}```"

        if len(res.result) > 4096:
            with io.BytesIO(str.encode(res.result)) as out_file:
                out_file.name = "result.txt"
                await client.send_file(chat.id, file=out_file)
                await e.edit(code)
            return

        await e.edit(output)


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.sendlog"))
@client.log_exception
async def send_logs(e):

    chat = await e.get_chat()

    if os.path.isdir("logs/"):
        files_in_dir = os.listdir("logs/")
        await client.send_from_disk(e, "logs/")
    else:
        await e.edit("`There are no logs saved!s`")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.exec\s+([\s\S]+)"))
async def py_execute(e):
    chat = await e.get_chat()
    code = e.pattern_match.group(1)

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    stdout, stderr, exc = None, None, None

    try:
        exec(code)
    except Exception:
        import traceback
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()

    sys.stdout = old_stdout
    sys.stderr = old_stderr

    if exc:
        await e.edit(f"**Query**:\n`{code}`\n\n **Exception:**\n`{exc}`")
        return

    if stderr:
        await e.edit(f"**Query**:\n`{code}`\n\n **Error:**\n`{stderr}`")
        return

    if stdout:
        if len(stdout) > 4096:
            with io.BytesIO(str.encode(stdout)) as out_file:
                out_file.name = "result.txt"
                await client.send_file(chat.id, file=out_file, caption=f"'{code}'")
                return

        await e.edit(f"**Query**:\n`{code}`\n\n **Result:**\n`{stdout}`")
    else:
        await e.edit("Did you forget to output something?")
