""" Anti-Flood Modulo de controle de Spam """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

import asyncio
import time

from pyrogram import filters
from pyrogram.types import ChatPermissions

from kannax import Message, get_collection, kannax

ANTIFLOOD_DATA = {}
ADMINS = {}
FLOOD_CACHE = {}

ANTI_FLOOD = get_collection("ANTIFLOOD")

LOG = kannax.getLogger(__name__)
CHANNEL = kannax.getCLogger(__name__)


async def _init() -> None:
    async for data in ANTI_FLOOD.find():
        ANTIFLOOD_DATA[data["chat_id"]] = {
            "data": data["data"],
            "limit": data["limit"],
            "mode": "Ban",
        }


async def cache_admins(msg):
    au_ids = []
    async for admins in msg.chat.iter_members(filter="administrators"):
        au_ids.append(admins.user.id)
    ADMINS[msg.chat.id] = au_ids


@kannax.on_cmd(
    "setflood",
    about={
        "header": "Defina o limite Anti-Flood para agir\n"
        "Pass <on/off> para desligar e ligaro turn Off and On.",
        "usage": "{tr}setflood 5\n"
        "{tr}setflood on (para ON)\n{tr}setflood off (para OFF)",
    },
    allow_private=False,
)
async def set_flood(msg: Message):
    """Set flood on/off e limite de flood"""
    args = msg.input_str
    if not args:
        await msg.err("leia .help setflood")
        return
    if "on" in args.lower():
        if (
            msg.chat.id in ANTIFLOOD_DATA
            and ANTIFLOOD_DATA[msg.chat.id].get("data") == "on"
        ):
            return await msg.err("Antiflood Já habilitado para este chat.")
        chat_limit = 5
        chat_mode = "Ban"
        if ANTIFLOOD_DATA.get(msg.chat.id):
            chat_limit = ANTIFLOOD_DATA[msg.chat.id].get("limit")
            chat_mode = ANTIFLOOD_DATA[msg.chat.id].get("mode")
        ANTIFLOOD_DATA[msg.chat.id] = {
            "data": "on",
            "limit": chat_limit,
            "mode": chat_mode,
        }
        await ANTI_FLOOD.update_one(
            {"chat_id": msg.chat.id},
            {"$set": {"data": "on", "limit": chat_limit, "mode": chat_mode}},
            upsert=True,
        )
        await msg.edit(
            "`Anti-Flood foi habilitado com sucesso...`", log=__name__, del_in=5
        )
    elif "off" in args.lower():
        if msg.chat.id not in ANTIFLOOD_DATA or (
            msg.chat.id in ANTIFLOOD_DATA
            and ANTIFLOOD_DATA[msg.chat.id].get("data") == "off"
        ):
            return await msg.err("Antiflood Já desativado para este bate-papo.")
        ANTIFLOOD_DATA[msg.chat.id]["data"] = "off"
        await ANTI_FLOOD.update_one(
            {"chat_id": msg.chat.id}, {"$set": {"data": "off"}}, upsert=True
        )
        await msg.edit(
            "`Anti-Flood foi desabilitado com sucesso...`", log=__name__, del_in=5
        )
    elif args.isnumeric():
        if msg.chat.id not in ANTIFLOOD_DATA or (
            msg.chat.id in ANTIFLOOD_DATA
            and ANTIFLOOD_DATA[msg.chat.id].get("data") == "off"
        ):
            return await msg.err("Primeiro ligue o ANTIFLOOD e, em seguida, defina o Limite.")
        input_ = int(args)
        if input_ < 3:
            await msg.err("Não é possível definir o Limite Antiflood inferior a 3")
            return
        ANTIFLOOD_DATA[msg.chat.id]["limit"] = input_
        await ANTI_FLOOD.update_one(
            {"chat_id": msg.chat.id}, {"$set": {"limit": input_}}, upsert=True
        )
        await msg.edit(
            f"`Anti-Flood  limite foi atualizado com sucesso para {input_}.`",
            log=__name__,
            del_in=5,
        )
    else:
        await msg.err("Argumento inválido, leia .help setflood")


@kannax.on_cmd(
    "setmode",
    about={
        "header": "Modo Anti-Flood",
        "description": "Quando o usuário atingiu o limite de flood "
        "Ele será banido/chutado/mutado pelos administradores de grupo",
        "usage": "{tr}setmode Ban\n{tr}setmode Kick\n{tr}setmode Mute",
    },
    allow_private=False,
)
async def set_mode(msg: Message):
    """Defina o modo de flood para agir"""
    mode = msg.input_str
    if not mode:
        await msg.err("leia .help setmode")
        return
    if msg.chat.id not in ANTIFLOOD_DATA or (
        msg.chat.id in ANTIFLOOD_DATA
        and ANTIFLOOD_DATA[msg.chat.id].get("data") == "off"
    ):
        return await msg.err("Primeiro ligue o ANTIFLOOD e, em seguida, defina o modo.")
    if mode.lower() in ("ban", "kick", "mute"):
        ANTIFLOOD_DATA[msg.chat.id]["mode"] = mode.lower()
        await ANTI_FLOOD.update_one(
            {"chat_id": msg.chat.id}, {"$set": {"mode": mode.lower()}}, upsert=True
        )
        await msg.edit(
            f"`Anti-Flood, O modo foi atualizado com sucesso para {mode.title()}`",
            log=__name__,
            del_in=5,
        )
    else:
        await msg.err("Argumento inválido, leia .help setmode")


@kannax.on_cmd(
    "vflood",
    about={"header": "Ver as configurações atuais de anti-flood", "usage": "{tr}vflood"},
    allow_private=False,
)
async def view_flood_settings(msg: Message):
    """ver as configurações atuais de inundação"""
    chat_data = ANTIFLOOD_DATA.get(msg.chat.id)
    if not chat_data or (chat_data and chat_data.get("data") == "off"):
        return await msg.err("Anti-Flood desativado neste chat.")
    limit = chat_data["limit"]
    mode = chat_data["mode"]
    await msg.edit(
        f"**Anti-Flood em {msg.chat.title}**\n"
        "\t\t**Habilitado:** `True`\n"
        f"\t\t**Limite:** `{limit}`\n"
        f"\t\t**Modo:** `{mode}`\n"
    )


@kannax.on_filters(
    filters.group & filters.incoming & ~filters.edited,
    group=3,
    check_restrict_perm=True,
)
async def anti_flood_handler(msg: Message):
    """Filtrando mensagens para lidar com flood"""

    if not msg.from_user:
        return

    chat_id = msg.chat.id
    user_id = msg.from_user.id
    first_name = msg.from_user.first_name

    if chat_id not in ANTIFLOOD_DATA or (
        chat_id in ANTIFLOOD_DATA and ANTIFLOOD_DATA[chat_id].get("data") == "off"
    ):
        return

    if not ADMINS.get(msg.chat.id):
        await cache_admins(msg)
    if user_id in ADMINS[chat_id]:
        if chat_id in FLOOD_CACHE:
            del FLOOD_CACHE[chat_id]
        return

    mode = ANTIFLOOD_DATA[msg.chat.id]["mode"]
    limit = ANTIFLOOD_DATA[msg.chat.id]["limit"]

    if check_flood(chat_id, user_id):
        if mode.lower() == "ban":
            await msg.client.kick_chat_member(chat_id, user_id)
            exec_str = "#BANNED"
        elif mode.lower() == "kick":
            await msg.client.kick_chat_member(chat_id, user_id, int(time.time() + 60))
            exec_str = "#KICKED"
        else:
            await msg.client.restrict_chat_member(chat_id, user_id, ChatPermissions())
            exec_str = "#MUTED"
        await asyncio.gather(
            msg.reply(
                r"\\**#KannaX_AntiFlood**//"
                "\n\nEste usuário atingiu seu limite de spam\n\n"
                f"**Usuario:** [{first_name}](tg://user?id={user_id})\n"
                f"**ID:** `{user_id}`\n**Limit:** `{limit}`\n\n"
                f"**Ação:** {exec_str}"
            ),
            CHANNEL.log(
                r"\\**#AntiFlood_Log**//"
                "\n\n**Limite anti-flood do usuário atingido**\n"
                f"**Usuario:** [{first_name}](tg://user?id={user_id})\n"
                f"**ID:** `{user_id}`\n**Limit:** {limit}\n"
                f"**Ação:** {exec_str} in {msg.chat.title}"
            ),
        )


def check_flood(chat_id: int, user_id: int):
    if not FLOOD_CACHE.get(chat_id) or FLOOD_CACHE[chat_id]["cur_user"] != user_id:
        FLOOD_CACHE[chat_id] = {"cur_user": user_id, "count": 1}
        return False
    chat_flood = FLOOD_CACHE[chat_id]
    count = chat_flood["count"]

    count += 1
    if count >= ANTIFLOOD_DATA[chat_id]["limit"]:
        del FLOOD_CACHE[chat_id]
        return True
    FLOOD_CACHE[chat_id] = {"cur_user": user_id, "count": count}
    return False
