import asyncio
import os
import time

import asyncssh
from telethon import events

from tg_companion import (ENABLE_SSH, SSH_HOSTNAME, SSH_KEY, SSH_PASSPHRASE,
                          SSH_PASSWORD, SSH_PORT, SSH_USERNAME, SUBPROCESS_ANIM)
from tg_companion.tgclient import client


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.term (.+)"))
@client.log_exception
async def terminal(e):

    cmd = e.pattern_match.group(1)

    await e.edit("`Connecting..`")

    start_time = time.time() + 10
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    OUTPUT = f"**QUERY:**\n__Command:__\n`{cmd}` \n__PID:__\n`{process.pid}`\n\n**Output:**\n"

    if not SUBPROCESS_ANIM:
        stdout, stderr = await process.communicate()

        if len(stdout) > 4096:
            await e.reply(f"{OUTPUT}\n__Process killed:__ `Messasge too long`")
            return

        await e.edit(f"{OUTPUT}`{stdout.decode()}`")
        return


    while process:
        if time.time() > start_time:
            process.kill()
            await e.edit(f"{OUTPUT}\n__Process killed__: `Time limit reached`")
            break

        stdout = await process.stdout.readline()

        if not stdout:
            _, stderr = await process.communicate()
            if stderr.decode():
                OUTPUT += f"`{stderr.decode()}`"
                await e.edit(OUTPUT)
                break

        if stdout:
            OUTPUT += f"`{stdout.decode()}`"

        if len(OUTPUT) > 4096:
            process.kill()
            await e.reply(f"{OUTPUT}\n__Process killed:__ `Messasge too long`")
            break
        try:
            await e.edit(OUTPUT)
        except Exception:
            break


@client.on(
    events.NewMessage(outgoing=True,
                      func=lambda x: ENABLE_SSH,
                      pattern="^\.rterm (.+)")
)
@client.log_exception
async def ssh_terminal(e):
    cmd = e.pattern_match.group(1)
    OUTPUT = f"**Query:**\n`{cmd}`\n\n**Output:**\n"
    await e.edit("`Connecting..`")

    async with asyncssh.connect(
        str(SSH_HOSTNAME),
        port=int(SSH_PORT),
        username=str(SSH_USERNAME),
        password=str(SSH_PASSWORD),
        passphrase=str(SSH_PASSPHRASE),
        client_keys=SSH_KEY,
        known_hosts=None,
    ) as conn:

        start_time = time.time() + 10
        async with conn.create_process(cmd) as process:
            if not SUBPROCESS_ANIM:
                stdout, stderr = await process.communicate()
                if not stdout:
                    await e.edit(f"{OUTPUT}`{stderr}`")
                    return
                if len(stdout) > 4096:
                    await e.reply("__Process killed:__ `Messasge too long`")
                    return
                await e.edit(f"{OUTPUT}`{stdout}`")
                return

            while True:
                if time.time() > start_time:
                    break

                stdout = await process.stdout.readline()

                if not stdout:
                    _, stderr = await process.communicate()
                    if stderr:
                        OUTPUT += f"`{stderr}`"
                        await e.edit(OUTPUT)
                        break

                if stdout:
                    OUTPUT += f"`{stdout}`"

                if len(OUTPUT) > 4096:
                    await e.reply("__Process killed:__ `Messasge too long`")
                    break
                try:
                    await e.edit(OUTPUT)
                except Exception:
                    break


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.upload (.+)"))
@client.log_exception
async def upload_file(e):
    to_upload = e.pattern_match.group(1)
    await client.send_from_disk(e, to_upload, force_document=True)


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.rupload (.+)"))
@client.log_exception
async def ssh_upload_file(e):
    to_upload = e.pattern_match.group(1)
    chat = await e.get_chat()
    await e.edit("`Connecting...`")

    async with asyncssh.connect(
            str(SSH_HOSTNAME),
            port=int(SSH_PORT),
            username=str(SSH_USERNAME),
            password=str(SSH_PASSWORD),
            passphrase=str(SSH_PASSPHRASE),
            client_keys=SSH_KEY,
            known_hosts=None) as conn:

        async with conn.create_process(f"test -f {to_upload} && echo 1") as process:
            stdout, _ = await process.communicate()
            if stdout:
                async with conn.start_sftp_client() as ftp:
                    await e.edit("`Downloading...`")
                    await ftp.get(to_upload, to_upload)
                    await client.send_from_disk(e, to_upload, force_document=True)

                os.remove(to_upload)
            else:
                await e.edit(f"__File Not Found__: `{to_upload}`")
