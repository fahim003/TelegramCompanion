from telethon import events
from telethon.tl.functions.contacts import BlockRequest

from tg_companion import BLOCK_PM, NOPM_SPAM
from tg_companion.tgclient import client, DB_URI
import sqlalchemy as db

PM_WARNS = {}


ACCEPTED_USERS = []

engine = db.create_engine(DB_URI)
metadata = db.MetaData()

private_messages_tbl = db.Table("private_messages", metadata,
                                db.Column("chat_id", db.Integer()))


connection = engine.connect()

metadata.create_all(
    bind=engine,
    tables=[private_messages_tbl],
    checkfirst=True)

db.insert(private_messages_tbl).values(chat_id=0)
query = db.select([private_messages_tbl])
load_privates = connection.execute(query).fetchall()
for row in load_privates:
    if row:
        ACCEPTED_USERS.append(row[0])


@client.on(events.NewMessage(incoming=True))
@client.log_exception
async def await_permission(e):
    global PM_WARNS
    global ACCEPTED_USERS

    if NOPM_SPAM is True and e.is_private:
        chat = await e.get_chat()
        if chat.id not in ACCEPTED_USERS:

            if chat.id not in PM_WARNS:
                PM_WARNS.update({chat.id: 0})

            if PM_WARNS[chat.id] == 3:
                await client.send_message(
                    chat.id,
                    message="You are spamming this user. I will ban you until he decides to unban you. Thanks ",
                )
                await client(BlockRequest(chat.id))
                return

            await client.send_message(
                chat.id,
                message="`Hi! This user will answer to your message soon. Please wait for his response and don't spam his PM. Thanks`",
            )

            PM_WARNS[chat.id] += 1


@client.on(events.NewMessage(outgoing=True, pattern=".approve"))
@client.log_exception
async def accept_permission(e):
    chat = await e.get_chat()
    if NOPM_SPAM is True and e.is_private:
        if chat.id not in ACCEPTED_USERS:

            if chat.id in PM_WARNS:
                del PM_WARNS[chat.id]
            connection = engine.connect()
            query = db.insert(private_messages_tbl).values(chat_id = chat.id)
            ACCEPTED_USERS.append(chat.id)
            connection.close()
            await e.edit("Private Message Accepted")
