""" system commands """
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

import asyncio
import shutil
import time

from pyrogram.types import User

from kannax import Config, Message, get_collection, kannax
from kannax.core.ext import RawClient
from kannax.utils import terminate

SAVED_SETTINGS = get_collection("CONFIGS")
DISABLED_CHATS = get_collection("DISABLED_CHATS")

MAX_IDLE_TIME = 300
LOG = kannax.getLogger(__name__)
CHANNEL = kannax.getCLogger(__name__)


async def _init() -> None:
    global MAX_IDLE_TIME  # pylint: disable=global-statement
    d_s = await SAVED_SETTINGS.find_one({"_id": "DYNO_SAVER"})
    if d_s:
        Config.RUN_DYNO_SAVER = bool(d_s["on"])
        MAX_IDLE_TIME = int(d_s["timeout"])
    disabled_all = await SAVED_SETTINGS.find_one({"_id": "DISABLE_ALL_CHATS"})
    if disabled_all:
        Config.DISABLED_ALL = bool(disabled_all["on"])
    else:
        async for i in DISABLED_CHATS.find():
            if i["_id"] == Config.LOG_CHANNEL_ID:
                continue
            Config.DISABLED_CHATS.add(i["_id"])


@kannax.on_cmd(
    "restart",
    about={
        "header": "Reinicia o bot e recarrega todos os plugins",
        "flags": {
            "-h": "reiniciar completamente",
            "-t": "limpa plugins carregados temporariamente",
            "-d": "limpa a pasta de trabalho",
        },
        "usage": "{tr}restart [flag | flags]",
        "examples": "{tr}restart -t -d",
    },
    del_pre=True,
    allow_channels=False,
)
async def restart_(message: Message):
    """restart KannaX"""
    await message.edit("`Reiniciando serviços do KannaX`", log=__name__)
    LOG.info("Serviços KannaX - Reinício iniciado")
    if "t" in message.flags:
        shutil.rmtree(Config.TMP_PATH, ignore_errors=True)
    if "d" in message.flags:
        shutil.rmtree(Config.DOWN_PATH, ignore_errors=True)
    if "h" in message.flags:
        if Config.HEROKU_APP:
            await message.edit(
                "`Heroku app detectado, tentando reiniciar o dyno...\nisso vai demorar até 30 segundos`",
                del_in=3,
            )
            Config.HEROKU_APP.restart()
            time.sleep(30)
        else:
            await message.edit("`Reiniciando [COMPLETO] ...`", del_in=1)
            asyncio.get_event_loop().create_task(kannax.restart(hard=True))
    else:
        await message.edit("`Reiniciando [RAPIDO] ...`", del_in=1)
        asyncio.get_event_loop().create_task(kannax.restart())


@kannax.on_cmd(
    "shutdown", about={"header": "Desligar o KannaX :)"}, allow_channels=False
)
async def shutdown_(message: Message) -> None:
    """shutdown KannaX"""
    await message.edit("`desligando ...`")
    if Config.HEROKU_APP:
        try:
            Config.HEROKU_APP.process_formation()["worker"].scale(0)
        except Exception as h_e:  # pylint: disable=broad-except
            await message.edit(f"**heroku error** : `{h_e}`")
            await asyncio.sleep(3)
    else:
        await asyncio.sleep(1)
    await message.delete()
    terminate()


@kannax.on_cmd(
    "die",
    about={
        "header": "definir tempo limite de desligamento automático do dyno heroku",
        "flags": {"-t": "inserir tempo limite off-line em minutos: padrão 5 min"},
        "usage": "{tr}die [flags]",
        "examples": ["{tr}die", "{tr}die -t5"],
    },
    allow_channels=False,
)
async def die_(message: Message) -> None:
    """set offline timeout to die KannaX"""
    global MAX_IDLE_TIME  # pylint: disable=global-statement
    if not Config.HEROKU_APP:
        await message.err("`app heroku não detectado !`")
        return
    await message.edit("`processando ...`")
    if Config.RUN_DYNO_SAVER:
        if isinstance(Config.RUN_DYNO_SAVER, asyncio.Task):
            Config.RUN_DYNO_SAVER.cancel()
        Config.RUN_DYNO_SAVER = False
        SAVED_SETTINGS.update_one(
            {"_id": "DYNO_SAVER"}, {"$set": {"on": False}}, upsert=True
        )
        await message.edit(
            "auto heroku dyno off worker has been **stopped**", del_in=5, log=__name__
        )
        return
    time_in_min = int(message.flags.get("-t", 5))
    if time_in_min < 5:
        await message.err(f"`please set higher value [{time_in_min}] !`")
        return
    MAX_IDLE_TIME = time_in_min * 60
    SAVED_SETTINGS.update_one(
        {"_id": "DYNO_SAVER"},
        {"$set": {"on": True, "timeout": MAX_IDLE_TIME}},
        upsert=True,
    )
    await message.edit(
        "auto heroku dyno off worker has been **started** " f"[`{time_in_min}`min]",
        del_in=3,
        log=__name__,
    )
    Config.RUN_DYNO_SAVER = asyncio.get_event_loop().create_task(_dyno_saver_worker())


@kannax.on_cmd(
    "setvar",
    about={
        "header": "defina vars no heroku",
        "usage": "{tr}setvar [var_name] [var_data]",
        "examples": "{tr}setvar BOT_MEDIA link",
    },
)
async def setvar_(message: Message) -> None:
    """set var (heroku)"""
    if not Config.HEROKU_APP:
        await message.err("`app heroku não detectado !`")
        return
    if not message.input_str:
        await message.err("`input needed !`")
        return
    var_name, var_data = message.input_str.split(maxsplit=1)
    if not var_data:
        await message.err("`var data needed !`")
        return
    var_name = var_name.strip()
    var_data = var_data.strip()
    heroku_vars = Config.HEROKU_APP.config()
    if var_name in heroku_vars:
        await CHANNEL.log(f"#HEROKU_VAR #SET #UPDATED\n\n`{var_name}` = `{var_data}`")
        await message.edit(
            f"`var {var_name} updated and forwarded to log channel !`", del_in=3
        )
    else:
        await CHANNEL.log(f"#HEROKU_VAR #SET #ADDED\n\n`{var_name}` = `{var_data}`")
        await message.edit(
            f"`var {var_name} added and forwarded to log channel !`", del_in=3
        )
    heroku_vars[var_name] = var_data


@kannax.on_cmd(
    "delvar",
    about={
        "header": "del var in heroku",
        "usage": "{tr}delvar [var_name]",
        "examples": "{tr}delvar WORKERS",
    },
)
async def delvar_(message: Message) -> None:
    """del var (heroku)"""
    if not Config.HEROKU_APP:
        await message.err("`app heroku não detectado !`")
        return
    if not message.input_str:
        await message.err("`var name needed !`")
        return
    var_name = message.input_str.strip()
    heroku_vars = Config.HEROKU_APP.config()
    if var_name not in heroku_vars:
        await message.err(f"`var {var_name} not found !`")
        return
    await CHANNEL.log(f"#HEROKU_VAR #DEL\n\n`{var_name}` = `{heroku_vars[var_name]}`")
    await message.edit(
        f"`var {var_name} deleted and forwarded to log channel !`", del_in=3
    )
    del heroku_vars[var_name]


@kannax.on_cmd(
    "getvar",
    about={
        "header": "get var in heroku",
        "usage": "{tr}getvar [var_name]",
        "examples": "{tr}getvar WORKERS",
    },
)
async def getvar_(message: Message) -> None:
    """get var (heroku)"""
    if not Config.HEROKU_APP:
        await message.err("`app heroku não detectado !`")
        return
    if not message.input_str:
        await message.err("`var name needed !`")
        return
    var_name = message.input_str.strip()
    heroku_vars = Config.HEROKU_APP.config()
    if var_name not in heroku_vars:
        await message.err(f"`var {var_name} not found !`")
        return
    await CHANNEL.log(f"#HEROKU_VAR #GET\n\n`{var_name}` = `{heroku_vars[var_name]}`")
    await message.edit(f"`var {var_name} forwarded to log channel !`", del_in=3)


@kannax.on_cmd(
    "enhere",
    about={
        "header": "enable userbot in disabled chat.",
        "flags": {"-all": "Enable Userbot in all chats."},
        "usage": "{tr}enhere [chat_id | username]\n{tr}enhere -all",
    },
)
async def enable_userbot(message: Message):
    if message.flags:
        if "-all" in message.flags:
            Config.DISABLED_ALL = False
            Config.DISABLED_CHATS.clear()
            await asyncio.gather(
                DISABLED_CHATS.drop(),
                SAVED_SETTINGS.update_one(
                    {"_id": "DISABLE_ALL_CHATS"}, {"$set": {"on": False}}, upsert=True
                ),
                message.edit("**Enabled** all chats!", del_in=5),
            )
        else:
            await message.err("invalid flag!")
    elif message.input_str:
        try:
            chat = await message.client.get_chat(message.input_str)
        except Exception as err:
            await message.err(str(err))
            return
        if chat.id not in Config.DISABLED_CHATS:
            await message.edit("this chat is already enabled!")
        else:
            Config.DISABLED_CHATS.remove(chat.id)
            await asyncio.gather(
                DISABLED_CHATS.delete_one({"_id": chat.id}),
                message.edit(
                    f"CHAT : `{chat.title}` removed from **DISABLED_CHATS**!",
                    del_in=5,
                    log=__name__,
                ),
            )
    else:
        await message.err("chat_id not found!")


@kannax.on_cmd(
    "dishere",
    about={
        "header": "disable userbot in current chat.",
        "flags": {"-all": "disable Userbot in all chats."},
        "usage": "{tr}dishere\n{tr}dishere [chat_id | username]\n{tr}dishere -all",
    },
)
async def disable_userbot(message: Message):
    if message.flags:
        if "-all" in message.flags:
            Config.DISABLED_ALL = True
            await asyncio.gather(
                SAVED_SETTINGS.update_one(
                    {"_id": "DISABLE_ALL_CHATS"}, {"$set": {"on": True}}, upsert=True
                ),
                message.edit("**Disabled** all chats!", del_in=5),
            )
        else:
            await message.err("invalid flag!")
    else:
        chat = message.chat
        if message.input_str:
            try:
                chat = await message.client.get_chat(message.input_str)
            except Exception as err:
                await message.err(str(err))
                return
        if chat.id in Config.DISABLED_CHATS:
            await message.edit("this chat is already disabled!")
        elif chat.id == Config.LOG_CHANNEL_ID:
            await message.err("can't disabled log channel")
        else:
            Config.DISABLED_CHATS.add(chat.id)
            await asyncio.gather(
                DISABLED_CHATS.insert_one({"_id": chat.id, "title": chat.title}),
                message.edit(
                    f"CHAT : `{chat.title}` added to **DISABLED_CHATS**!",
                    del_in=5,
                    log=__name__,
                ),
            )


@kannax.on_cmd("listdisabled", about={"header": "List all disabled chats."})
async def view_disabled_chats_(message: Message):
    if Config.DISABLED_ALL:
        # bot will not print this, but dont worry except log channel
        await message.edit("All chats are disabled!", del_in=5)
    elif not Config.DISABLED_CHATS:
        await message.edit("**DISABLED_CHATS** not found!", del_in=5)
    else:
        out_str = "🚷 **DISABLED_CHATS** 🚷\n\n"
        async for chat in DISABLED_CHATS.find():
            out_str += f" 👥 {chat['title']} 🆔 `{chat['_id']}`\n"
        await message.edit(out_str, del_in=0)


@kannax.on_cmd(
    "sleep (\\d+)",
    about={"header": "sleep KannaX :P", "usage": "{tr}sleep [timeout in seconds]"},
    allow_channels=False,
)
async def sleep_(message: Message) -> None:
    """sleep KannaX"""
    seconds = int(message.matches[0].group(1))
    await message.edit(f"`sleeping {seconds} seconds...`")
    asyncio.get_event_loop().create_task(_slp_wrkr(seconds))


async def _slp_wrkr(seconds: int) -> None:
    await kannax.stop()
    await asyncio.sleep(seconds)
    await kannax.reload_plugins()
    await kannax.start()


@kannax.on_user_status()
async def _user_status(_, user: User) -> None:
    Config.STATUS = user.status


@kannax.add_task
async def _dyno_saver_worker() -> None:
    count = 0
    check_delay = 5
    offline_start_time = time.time()
    while Config.RUN_DYNO_SAVER:
        if not count % check_delay and (
            Config.STATUS is None or Config.STATUS != "online"
        ):
            if Config.STATUS is None:
                LOG.info("< bot client found ! >")
            else:
                LOG.info("< state changed to offline ! >")
                offline_start_time = time.time()
            warned = False
            while Config.RUN_DYNO_SAVER and (
                Config.STATUS is None or Config.STATUS != "online"
            ):
                if not count % check_delay:
                    if Config.STATUS is None:
                        offline_start_time = RawClient.LAST_OUTGOING_TIME
                    current_idle_time = int((time.time() - offline_start_time))
                    if current_idle_time < 5:
                        warned = False
                    if current_idle_time >= MAX_IDLE_TIME:
                        try:
                            Config.HEROKU_APP.process_formation()["worker"].scale(0)
                        except Exception as h_e:  # pylint: disable=broad-except
                            LOG.error(f"heroku app error : {h_e}")
                            offline_start_time += 20
                            await asyncio.sleep(10)
                            continue
                        LOG.info("< successfully killed heroku dyno ! >")
                        await CHANNEL.log("heroku dyno killed !")
                        terminate()
                        return
                    prog = round(current_idle_time * 100 / MAX_IDLE_TIME, 2)
                    mins = int(MAX_IDLE_TIME / 60)
                    if prog >= 75 and not warned:
                        rem = int((100 - prog) * MAX_IDLE_TIME / 100)
                        await CHANNEL.log(
                            f"#WARNING\n\ndyno kill worker `{prog}%` completed !"
                            f"\n`{rem}`s remaining !"
                        )
                        warned = True
                    LOG.info(f"< dyno kill worker ... ({prog}%)({mins}) >")
                await asyncio.sleep(1)
                count += 1
            LOG.info("< state changed to online ! >")
        await asyncio.sleep(1)
        count += 1
    if count:
        LOG.info("< auto heroku dyno off worker has been stopped! >")
