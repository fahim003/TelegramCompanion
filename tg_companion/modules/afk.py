from telethon import events

from tg_companion.tgclient import client

USER_AFK = {}


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.afk?(.+)"))
@client.log_exception
async def afk(e):
    reason = e.pattern_match.group(1)
    if len(reason) <= 2:
        reason = ""
    if not USER_AFK:
        USER_AFK.update({"yes": reason})
        if reason:
            await e.edit(f"**I will be afk for a while. \n __Reason__: {reason}")
            return

        await e.edit(f"**I will be afk for a while.")
        raise events.StopPropagation


@client.on(events.NewMessage(outgoing=True))
@client.log_exception
async def no_afk(e):
    chat = await e.get_chat()
    if "yes" in USER_AFK:
        await client.send_message(chat.id, "`I'm no longer afk`")
        del USER_AFK["yes"]


@client.log_exception
async def reply_afk(e):
    chat = await e.get_chat()
    reason = USER_AFK["yes"]
    if e.mentioned or e.is_private:
        if USER_AFK:
            if not reason:
                await client.send_message(chat.id, "**I'm afk and I will be back soon**", reply_to=e.id)
                return

            await client.send_message(chat.id, f"**I'm afk and I will be back soon**\n__Reason:__: {reason}", reply_to=e.id)
