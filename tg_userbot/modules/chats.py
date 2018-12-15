from tg_userbot import client
from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.tl.functions.channels import EditPhotoRequest
from telethon.tl.functions.channels import EditAboutRequest
from telethon.tl.functions.channels import UpdateUsernameRequest
from telethon.tl.functions.channels import EditTitleRequest

from telethon import errors
from telethon.errors.rpcerrorlist import UsernameOccupiedError
import io
import re
import os


@client.on(events.NewMessage(outgoing=True, pattern='^.cpic'))
async def update_profile_pic(e):
    if e.reply_to_msg_id:
        message = await e.get_reply_message()
        photo = None
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                await e.edit('`DOWNLOADING`')
                photo = await client.download_media(message.photo)

            elif isinstance(message.media, MessageMediaDocument):
                mime_type = message.media.document.mime_type.split('/')
                media_type = mime_type[0]
                media_ext = mime_type[1]

                if media_type == 'image':
                    await e.edit('`DOWNLOADING`')
                    photo = await client.download_file(message.media.document)
                    photo = io.BytesIO(photo)
                    photo.name = 'image.' + media_ext

            else:
                await e.edit('`The type of this media entity is invalid.`')

        if photo:
            await e.edit('`UPLOADING`')
            file = await client.upload_file(photo)
            try:
                await client(EditPhotoRequest(e.chat_id, file))
                await e.edit('`Channel picture changed`')

            except Exception as exc:
                if isinstance(exc, errors.ChatAdminRequiredError):
                    await e.edit('`Chat admin privileges are required to do that`')

                if isinstance(exc, errors.PhotoInvalidError):
                    await e.edit('`The selected photo is invalid`')

            if isinstance(photo, str):
                os.remove(photo)


@client.on(events.NewMessage(outgoing=True, pattern='^.cabout (.+)'))
async def update_profile_bio(e):
    about = e.pattern_match.group(1)
    if len(about) > 255:
        await e.edit('`Channel about is too long.`')

    else:
        try:
            await client(EditAboutRequest(e.chat.id, about))
            await e.edit('`Succesfully changed chat about`')

        except Exception as exc:
            if isinstance(exc, ChatAboutNotModifiedError):
                await e.edit('`About text has not changed.`')

            if isinstance(exc, errors.ChatAdminRequiredError):
                await e.edit('`Chat admin privileges are required to do that`')

            if isinstance(exc, errors.ChatNotModifiedError):
                await e.edit("`The chat wasn't modified`")


@client.on(events.NewMessage(outgoing=True, pattern='^.cuname (.+)'))
async def change_profile_username(e):
    username = e.pattern_match.group(1)

    if '@' in username:
        username = username[1:]

    allowed_char = re.match(r"[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]", username)

    if not allowed_char:
        await e.edit('`Invalid Username`')

    elif len(username) > 30:
        await e.edit('`Channel username is too long.`')

    elif len(username) < 5:
        await e.edit('`Channel username is too short`')

    else:
        try:
            await client(UpdateUsernameRequest(e.chat.id, username))
            await e.edit('`Succesfully changed channel username`')

        except Exception as exc:
            if isinstance(exc, errors.AdminsTooMuchError):
                await e.edit("`You're admin of too many public channels, make some channels private to change the username of this channel.`")

            if isinstance(exc, errors.ChatAdminRequiredError):
                await e.edit("Chat admin privileges are required to do that")

            if isinstance(exc, errors.UsernameOccupiedError):
                await e.edit(f'`{username} is already taken`')

            if isinstance(exc, errors.ChatNotModifiedError):
                await e.edit("`The chat or channel wasn't modified`")


@client.on(events.NewMessage(outgoing=True, pattern='.name (.+)'))
async def change_profile_name(e):
    title = e.pattern_match.group(1)
    try:
        await client(EditTitleRequest(e.chat.id, title))
        await e.edit('`Succesfully changed channel/chat title`')

    except Exception as exc:
        if isinstance(exc, errors.ChatAdminRequiredError):
            await e.edit('`Chat admin privileges are required to do that`')

        if isinstance(exc, errors.ChatNotModifiedError):
            await e.edit("`The chat or channel wasn't modified`")
