from tg_companion import STATS_TIMER
from tg_companion.tgclient import DB_URI, LOGGER, client
from telethon import events
from telethon import utils
from telethon.tl.functions.channels import GetFullChannelRequest
import sqlalchemy as db

import time
import progressbar


engine = db.create_engine(DB_URI)
metadata = db.MetaData()

stats_tbl = db.Table("stats", metadata,
                     db.Column("updatetime", db.String(), primary_key=True),

                     db.Column("totaldialogs", db.Integer()),

                     db.Column("usercount", db.Integer()),

                     db.Column("channelcount", db.Integer()),

                     db.Column("supcount", db.Integer()),

                     db.Column("convertedgroups", db.Integer()),

                     db.Column("numchannel", db.Integer()),

                     db.Column("numuser", db.Integer()),

                     db.Column("numdeleted", db.Integer()),

                     db.Column("numbot", db.Integer()),

                     db.Column("numchat", db.Integer()),
                     db.Column("numsuper", db.Integer()),
                     )

GroupsInfo_tbl = db.Table("groups_info", metadata,
                          db.Column("supergroupid", db.Integer()),
                          db.Column("oldgroupid", db.Integer()))

FirstRun = None


@client.on_timer(STATS_TIMER)
@client.log_exception
async def GetStats():
    global FirstRun

    TotalDialogs = 0
    UserCount = 0
    ChannelCount = 0
    SupCount = 0
    ConvertedGroupsIDs = []
    NewGroupsIDs = []
    NumChannel = 0
    NumUser = 0
    NumBot = 0
    NumDeleted = 0
    NumChat = 0
    NumSuper = 0

    FirstTimeRunning = None

    UpdateTime = time.strftime("%c")

    connection = engine.connect()
    if not engine.dialect.has_table(engine, stats_tbl):
        metadata.create_all(
            bind=engine, tables=[
                stats_tbl, GroupsInfo_tbl])
    connection.close()

    connection = engine.connect()
    query = db.select([stats_tbl])
    if not connection.execute(query).fetchall():
        FirstTimeRunning = True

    if FirstRun:
        LOGGER.info(
            "Gathering Stats. You'll be able to use this app during this process without problems"
        )
        LOGGER.info("The companion may not respond to your command for 5 second. Don't panic and try again if your command didn't worked")

        LOGGER.info("You can disable this in the config.env file")

        if FirstTimeRunning:
            LOGGER.info(
                "Because this is your first time running this, the .stats command won't work until this process isn't over"
            )

    else:
        LOGGER.info("Updating Stats...")
        LOGGER.info("The companion may not respond to your command for 5 second. Don't panic and try again if your command didn't worked")

    CachedSupergroups = []

    if not FirstTimeRunning:
        connection = engine.connect()
        query = db.select([GroupsInfo_tbl.columns.supergroupid])
        result = connection.execute(query).fetchall()
        for row in result:
            CachedSupergroups.append(row[0])
        connection.close()

    UserId = await client.get_me()
    UserId = UserId.id

    dialogs = await client.get_dialogs(limit=None)
    for dialog in dialogs:
        if dialog.is_group:
            NumChat = NumChat + 1
        if dialog.is_user:
            if dialog.entity.bot:
                NumBot = NumBot + 1
            else:
                NumUser = NumUser + 1
        if dialog.is_channel:
            if dialog.is_group:
                NumSuper = NumSuper + 1
            else:
                NumChannel = NumChannel + 1
    completed = 0
    bar = progressbar.ProgressBar(
        max_value=NumSuper,
        widget=None,
        poll_interval=1)
    bar.update(completed)
    for dialog in dialogs:
        if dialog.is_channel:
            if dialog.is_group:
                ID1 = utils.get_peer_id(
                    utils.get_input_peer(
                        dialog, allow_self=False))
                strid = str(ID1).replace("-100", "")
                ID = int(strid)
                if ID not in CachedSupergroups:
                    ent = await client.get_input_entity(ID1)
                    gotChatFull = await client(GetFullChannelRequest(ent))

                    connection = engine.connect()

                    query = db.insert(GroupsInfo_tbl).values(
                        supergroupid=gotChatFull.full_chat.id,
                        oldgroupid=gotChatFull.full_chat.migrated_from_chat_id)

                    connection.execute(query)
                    connection.close()

    LookIds = []

    for dialog in dialogs:
        ID = None
        try:
            ID = utils.get_peer_id(
                utils.get_input_peer(
                    dialog, allow_self=False))
        except Exception:
            ID = UserId
        if dialog.is_channel:
            strid = str(ID).replace("-100", "")
            ID = int(strid)
        elif dialog.is_group:
            strid = str(ID).replace("-", "")
            ID = int(strid)
        LookIds.append(ID)

    for dialog in dialogs:
        if dialog.is_group:
            ID = utils.get_peer_id(
                utils.get_input_peer(
                    dialog, allow_self=False))
            strid = str(ID).replace("-100", "")
            ID = int(strid)

            connection = engine.connect()
            query = db.select(
                [GroupsInfo_tbl]).where(
                GroupsInfo_tbl.columns.supergroupid == ID)
            exec = connection.execute(query)
            result = exec.fetchall()
            connection.close()
            for row in result:
                if row[1] is not None:
                    NewGroupsIDs.append(row[0])
                    ConvertedGroupsIDs.append(row[1])
    bar.finish()

    print("Counting your chats...")

    for dialog in dialogs:
        try:
            ID = utils.get_peer_id(
                utils.get_input_peer(
                    dialog, allow_self=False))
        except Exception:
            ID = UserId
        if dialog.is_channel:
            strid = str(ID).replace("-100", "")
            ID = int(strid)
        elif dialog.is_group:
            strid = str(ID).replace("-", "")
            ID = int(strid)
        if utils.get_display_name(dialog.entity) == "":
            NumDeleted = NumDeleted + 1
        elif ID == UserId:
            pass
        if ID not in ConvertedGroupsIDs:
            ent = await client.get_input_entity(dialog)
            msgs = await client.get_messages(ent, limit=0)
            count = msgs.total
            if dialog.is_channel:
                if dialog.entity.megagroup:
                    SupCount = SupCount + count
                else:
                    ChannelCount = ChannelCount + count
            elif dialog.is_group and dialog.is_user:
                UserCount = UserCount + count
        if ID in NewGroupsIDs:
            if ID in LookIds and ID not in ConvertedGroupsIDs:
                index = NewGroupsIDs.index(ID)
                ent = await client.get_input_entity(int("-" + str(ConvertedGroupsIDs[index])))
                msgs = await client.get_messages(ent)
                OldChatCount = msgs.total
                UserCount = UserCount + OldChatCount

    ConvertedCount = len(NewGroupsIDs)
    NumChat = NumChat - ConvertedCount
    TotalDialogs = UserCount + ChannelCount + SupCount

    connection = engine.connect()
    query = db.select([stats_tbl.columns.updatetime])

    if not connection.execute(query).fetchall():
        query = db.insert(stats_tbl).values(
            updatetime=UpdateTime,
            totaldialogs=TotalDialogs,
            usercount=UserCount,
            channelcount=ChannelCount,
            supcount=SupCount,
            convertedgroups=ConvertedCount,
            numchannel=NumChannel,
            numuser=NumUser,
            numdeleted=NumDeleted,
            numbot=NumBot,
            numchat=NumChat,
            numsuper=NumSuper,
        )
    else:
        query = db.update(stats_tbl).values(
            updatetime=UpdateTime,
            totaldialogs=TotalDialogs,
            usercount=UserCount,
            channelcount=ChannelCount,
            supcount=SupCount,
            convertedgroups=ConvertedCount,
            numchannel=NumChannel,
            numuser=NumUser,
            numdeleted=NumDeleted,
            numbot=NumBot,
            numchat=NumChat,
            numsuper=NumSuper,
        )
    connection.execute(query)
    connection.close()

    LOGGER.info("DONE!! You can see your stats by sending .stats in any chat")


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.stats"))
@client.log_exception
async def show_stats(e):
    stats = None

    connection = engine.connect()
    query = db.select([stats_tbl])
    result = connection.execute(query).fetchall()
    if result:
        stats = result[0]
    connection.close()

    if stats:
        updatetime, totaldialogs, usercount, channelcount, supcount, convertedgroups, numchannel, numuser, numdeleted, numbot, numchat, numsuper = (
            stats
        )

        if convertedgroups != 0:
            if convertedgroups != numsuper:
                convertedgroups = convertedgroups
            else:
                convertedgroups = "all"
        else:
            convertedgroups = None

        REPLY = f"""

    **\nMESSAGES COUNTS:**
    Normal groups and chats: `{usercount}`
    Channels: `{channelcount}`
    Supergroups: `{supcount}`
    TOTAL MESSAGES: `{totaldialogs}`

    **\nCHAT COUNTS:**
    Number of Channels: `{numchannel}`
    Number of Supergroups: `{numsuper}` from where `{convertedgroups}` of them converted from normal groups.
    Number of Normal groups: `{numchat}`
    Number of Private conversations: `{numuser}` from where `{numdeleted}` are now Deleted Accounts.
    Number of Bot conversations:  `{numbot}`
    Last Update Time :  `{updatetime}`
    """

        await e.edit(REPLY)
    else:
        await e.edit("`Stats are unavailable!! Try again later. `")
