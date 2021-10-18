""" configurar gban """

import asyncio
from typing import Union

import spamwatch
from pyrogram.errors import (
    ChannelInvalid,
    ChatAdminRequired,
    PeerIdInvalid,
    UserAdminInvalid,
)
from spamwatch.types import Ban

from kannax import Config, Message, filters, get_collection, pool, kannax
from kannax.utils import get_response, mention_html, is_dev

SAVED_SETTINGS = get_collection("CONFIGS")
GBAN_USER_BASE = get_collection("GBAN_USER")
WHITELIST = get_collection("WHITELIST_USER")
CHANNEL = kannax.getCLogger(__name__)
LOG = kannax.getLogger(__name__)


async def _init() -> None:
    s_o = await SAVED_SETTINGS.find_one({"_id": "ANTISPAM_ENABLED"})
    i_as = await SAVED_SETTINGS.find_one({"_id": "SPAM_PROTECTION"})
    if s_o:
        Config.ANTISPAM_SENTRY = s_o["data"]
    if i_as:
        Config.SPAM_PROTECTION = s_o["data"]


@kannax.on_cmd(
    "antispam",
    about={
        "header": "habilitar / desabilitar antispam",
        "description": "Alternar API Auto Bans, baseado em Combot Cas Api",
    },
    allow_channels=False,
)
async def antispam_(message: Message):
    """habilitar / desabilitar antispam"""
    if Config.ANTISPAM_SENTRY:
        Config.ANTISPAM_SENTRY = False
        await message.edit("`antispam desativado !`", del_in=3)
    else:
        Config.ANTISPAM_SENTRY = True
        await message.edit("`antispam ativado !`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {"_id": "ANTISPAM_ENABLED"},
        {"$set": {"data": Config.ANTISPAM_SENTRY}},
        upsert=True,
    )


@kannax.on_cmd(
    "spamprotection",
    about={
        "header": "habilitar / desabilitar Proteção contra spam Intellivoid",
        "description": "Alternar APIs Auto Bans, com base na API de proteção contra spam Intellivoid",
    },
    allow_channels=False,
)
async def spam_protect_(message: Message):
    """habilitar / desabilitar Proteção contra spam Intellivoid"""
    if Config.SPAM_PROTECTION:
        Config.SPAM_PROTECTION = False
        await message.edit("`Proteção contra spam Intellivoid desativado !`", del_in=3)
    else:
        Config.SPAM_PROTECTION = True
        await message.edit("`Proteção contra spam Intellivoid ativado !`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {"_id": "SPAM_PROTECTION"},
        {"$set": {"data": Config.SPAM_PROTECTION}},
        upsert=True,
    )


@kannax.on_cmd(
    "gban",
    about={
        "header": "Banir um usuário globalmente",
        "description": "Adiciona o usuário à sua lista GBan. "
        "Bane um usuário globalmente banido se ele entrar ou enviar uma mensagem. "
        "[NOTA: Funciona apenas em grupos em que você é administrador.]",
        "examples": "{tr}gban [userid | reply] [reason for gban] (mandatory)",
    },
    allow_channels=False,
    allow_bots=False,
)
async def gban_user(message: Message):
    """banir um usuário globalmente"""
    await message.edit("`GBanning...`")
    user_id, reason = message.extract_user_and_text
    if is_dev(user_id):
        await message.reply("`Lol ele é meu desenvolvedor porque iria bani-lo?.`")
        return
    if not user_id:
        await message.edit(
            "`nenhum user_id ou mensagem válida especificada,`"
            "`não digite .help gban para mais informações. "
            "`Porque ninguém vai te ajudar`(｡ŏ_ŏ) ⚠",
            del_in=0,
        )
        return
    get_mem = await message.client.get_user_dict(user_id)
    firstname = get_mem["fname"]
    if not reason:
        await message.edit(
            f"**#Abortado**\n\n**Gbanning** of {mention_html(user_id, firstname)} "
            "Abortado coz Nenhum motivo do gban fornecido pelo banner",
            del_in=5,
        )
        return
    user_id = get_mem["id"]
    if user_id == (await message.client.get_me()).id:
        await message.edit(r"Lol. Por que eu vou banir a mim mesmo ¯\(°_o)/¯")
        return
    if user_id in Config.SUDO_USERS:
        await message.edit(
            "Esse usuário está na minha Lista de Sudo, portanto, não posso bani-lo.\n\n"
            "**Tip:** Remova-os da Lista de Sudo e tente novamente. (¬_¬)",
            del_in=5,
        )
        return
    found = await GBAN_USER_BASE.find_one({"user_id": user_id})
    if found:
        await message.edit(
            "**#Already_GBanned**\n\nO usuário já existe na minha lista Gban.\n"
            f"**Razão para GBan:** `{found['reason']}`",
            del_in=5,
        )
        return
    await message.edit(
        r"\\**#GBanned_User**//"
        f"\n\n**Primeiro Nome:** {mention_html(user_id, firstname)}\n"
        f"**User ID:** `{user_id}`\n**Razão:** `{reason}`"
    )
    # TODO: podemos adicionar algo como "GBanned por {any_sudo_user_fname}"
    if message.client.is_bot:
        chats = [message.chat]
    else:
        chats = await message.client.get_common_chats(user_id)
    gbanned_chats = []
    for chat in chats:
        try:
            await chat.kick_member(user_id)
            gbanned_chats.append(chat.id)
            await CHANNEL.log(
                r"\\**#Antispam_Log**//"
                f"\n**User:** {mention_html(user_id, firstname)}\n"
                f"**User ID:** `{user_id}`\n"
                f"**Chat:** {chat.title}\n"
                f"**Chat ID:** `{chat.id}`\n"
                f"**Razão:** `{reason}`\n\n$GBAN #id{user_id}"
            )
        except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid):
            pass
    await GBAN_USER_BASE.insert_one(
        {
            "firstname": firstname,
            "user_id": user_id,
            "razão": reason,
            "chat_ids": gbanned_chats,
        }
    )
    if message.reply_to_message:
        await CHANNEL.fwd_msg(message.reply_to_message)
        await CHANNEL.log(f"$GBAN #prid{user_id} ⬆️")
    LOG.info("G-Banned %s", str(user_id))


@kannax.on_cmd(
    "ungban",
    about={
        "header": "Desbanir um usuário globalmente",
        "description": "Remove um usuário da sua lista Gban",
        "examples": "{tr}ungban [userid | reply]",
    },
    allow_channels=False,
    allow_bots=False,
)
async def ungban_user(message: Message):
    """desbane um usuário globalmente"""
    await message.edit("`UnGBanning...`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.err("user-id not found")
        return
    try:
        get_mem = await message.client.get_user_dict(user_id)
    except PeerIdInvalid:
        await GBAN_USER_BASE.find_one_and_delete({"user_id": user_id})
        deleted_user_ = f"\nRemovido [Deleted Account !](tg://openmessage?user_id={user_id}) com sucesso"
        return await message.edit(
            r"\\**#UnGbanned_User**//" + "\n" + deleted_user_, log=__name__
        )
    firstname = get_mem["fname"]
    user_id = get_mem["id"]
    found = await GBAN_USER_BASE.find_one_and_delete({"user_id": user_id})
    if not found:
        await message.err("Usuário não encontrado na minha lista Gban")
        return
    if "chat_ids" in found:
        for chat_id in found["chat_ids"]:
            try:
                await kannax.unban_chat_member(chat_id, user_id)
                await CHANNEL.log(
                    r"\\**#Antispam_Log**//"
                    f"\n**User:** {mention_html(user_id, firstname)}\n"
                    f"**User ID:** `{user_id}`\n\n"
                    f"$UNGBAN #id{user_id}"
                )
            except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid):
                pass
    await message.edit(
        r"\\**#UnGbanned_User**//"
        f"\n\n**Primeiro Nome:** {mention_html(user_id, firstname)}\n"
        f"**User ID:** `{user_id}`"
    )
    LOG.info("UnGbanned %s", str(user_id))


@kannax.on_cmd(
    "glist",
    about={
        "header": "Obtenha uma lista de usuários Gbanned",
        "description": "Obtenha uma lista atualizada de usuários banidos por você.",
        "examples": "Lol. Basta digitar {tr}glist",
    },
    allow_channels=False,
)
async def list_gbanned(message: Message):
    """vies gbanned users"""
    msg = ""
    bad_users = ""
    async for c in GBAN_USER_BASE.find():
        try:
            msg += (
                "**User** : "
                + str(c["firstname"])
                + "-> with **User ID** -> "
                + str(c["user_id"])
                + " is **GBanned for** : "
                + str(c["reason"])
                + "\n\n"
            )
        except KeyError:
            await GBAN_USER_BASE.delete_one(c)
            bad_users += (
                "**User** : "
                + str(c["firstname"])
                + "-> with **User ID** -> "
                + str(c["user_id"])
            )

    await message.edit_or_send_as_file(
        f"**--Lista de usuários banidos globalmente--**\n\n{msg}" if msg else "`glist vazia!`"
    )
    if bad_users:
        await CHANNEL.log(
            "**Esses usuários foram removidos da lista gban devido a alguns erros no motivo do gban!"
            " você pode bani-los novamente manualmente**\n" + bad_users
        )


@kannax.on_cmd(
    "whitelist",
    about={
        "header": "Coloque um usuário na whitelist",
        "description": "Use whitelist para adicionar usuários para contornar banimentos de API",
        "useage": "{tr}whitelist [userid | reply to user]",
        "examples": "{tr}whitelist 5231147869",
    },
    allow_channels=False,
    allow_bots=False,
)
async def whitelist(message: Message):
    """add user to whitelist"""
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.err("user-id not found")
        return
    get_mem = await message.client.get_user_dict(user_id)
    firstname = get_mem["fname"]
    user_id = get_mem["id"]
    found = await WHITELIST.find_one({"user_id": user_id})
    if found:
        await message.err("User Already in My WhiteList")
        return
    await asyncio.gather(
        WHITELIST.insert_one({"firstname": firstname, "user_id": user_id}),
        message.edit(
            r"\\**#Whitelisted_User**//"
            f"\n\n**Primeiro Nome:** {mention_html(user_id, firstname)}\n"
            f"**User ID:** `{user_id}`"
        ),
        CHANNEL.log(
            r"\\**#Antispam_Log**//"
            f"\n**User:** {mention_html(user_id, firstname)}\n"
            f"**User ID:** `{user_id}`\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Chat ID:** `{message.chat.id}`\n\n$WHITELISTED #id{user_id}"
        ),
    )
    LOG.info("WhiteListed %s", str(user_id))


@kannax.on_cmd(
    "rmwhite",
    about={
        "header": "Remove o usuario da Whitelist",
        "description": "Use-o para remover usuários de WhiteList",
        "useage": "{tr}rmwhite [userid | reply to user]",
        "examples": "{tr}rmwhite 5231147869",
    },
    allow_channels=False,
    allow_bots=False,
)
async def rmwhitelist(message: Message):
    """remover um usuário da whitelist"""
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.err("user-id not found")
        return
    get_mem = await message.client.get_user_dict(user_id)
    firstname = get_mem["fname"]
    user_id = get_mem["id"]
    found = await WHITELIST.find_one({"user_id": user_id})
    if not found:
        await message.err("Usuário não encontrado em minha WhiteList")
        return
    await asyncio.gather(
        WHITELIST.delete_one({"firstname": firstname, "user_id": user_id}),
        message.edit(
            r"\\**#Removed_Whitelisted_User**//"
            f"\n\n**Primeiro Nome:** {mention_html(user_id, firstname)}\n"
            f"**User ID:** `{user_id}`"
        ),
        CHANNEL.log(
            r"\\**#Antispam_Log**//"
            f"\n**User:** {mention_html(user_id, firstname)}\n"
            f"**User ID:** `{user_id}`\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Chat ID:** `{message.chat.id}`\n\n$RMWHITELISTED #id{user_id}"
        ),
    )
    LOG.info("WhiteListed %s", str(user_id))


@kannax.on_cmd(
    "listwhite",
    about={
        "header": "Obtenha uma lista de usuários permitidos",
        "description": "Obtenha uma lista atualizada de usuários na Lista Branca por você.",
        "examples": "Lol. Basta digitar {tr}listwhite",
    },
    allow_channels=False,
)
async def list_white(message: Message):
    """list whitelist"""
    msg = ""
    async for c in WHITELIST.find():
        msg += (
            "**User** : "
            + str(c["firstname"])
            + "-> with **User ID** -> "
            + str(c["user_id"])
            + "\n\n"
        )

    await message.edit_or_send_as_file(
        f"**--Lista de usuários permitidos--**\n\n{msg}" if msg else "`whitelist vazia!`"
    )


@kannax.on_filters(
    filters.group & filters.new_chat_members, group=1, check_restrict_perm=True
)
async def gban_at_entry(message: Message):
    """handle gbans"""
    chat_id = message.chat.id
    for user in message.new_chat_members:
        user_id = user.id
        firstname = user.first_name
        if await WHITELIST.find_one({"user_id": user_id}):
            continue
        gbanned = await GBAN_USER_BASE.find_one({"user_id": user_id})
        if gbanned:
            if "chat_ids" in gbanned:
                chat_ids = gbanned["chat_ids"]
                chat_ids.append(chat_id)
            else:
                chat_ids = [chat_id]
            await asyncio.gather(
                message.client.kick_chat_member(chat_id, user_id),
                message.reply(
                    r"\\**#𝑿_Antispam**//"
                    "\n\nUsuário banido globalmente detectado neste bate-papo.\n\n"
                    f"**User:** {mention_html(user_id, firstname)}\n"
                    f"**ID:** `{user_id}`\n**Razão:** `{gbanned['reason']}`\n\n"
                    "**Ação rápida:** Banido",
                    del_in=10,
                ),
                CHANNEL.log(
                    r"\\**#Antispam_Log**//"
                    "\n\n**GBanned User $SPOTTED**\n"
                    f"**User:** {mention_html(user_id, firstname)}\n"
                    f"**ID:** `{user_id}`\n**Razão:** {gbanned['reason']}\n**Ação rápida:** "
                    f"Banido em {message.chat.title}"
                ),
                GBAN_USER_BASE.update_one(
                    {"user_id": user_id, "firstname": firstname},
                    {"$set": {"chat_ids": chat_ids}},
                    upsert=True,
                ),
            )
        elif Config.ANTISPAM_SENTRY:
            try:
                res = await get_response.json(
                    f"https://api.cas.chat/check?user_id={user_id}"
                )
            except ValueError:  # api down
                pass
            else:
                if res and (res["ok"]):
                    reason = (
                        " | ".join(res["result"]["messages"])
                        if "result" in res
                        else None
                    )
                    await asyncio.gather(
                        message.client.kick_chat_member(chat_id, user_id),
                        message.reply(
                            r"\\**#𝑿_Antispam**//"
                            "\n\nUsuário banido globalmente detectado neste bate-papo.\n\n"
                            "**$SENTRY CAS Federation Ban**\n"
                            f"**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n\n"
                            "**Ação Rápida:** Banido",
                            del_in=10,
                        ),
                        CHANNEL.log(
                            r"\\**#Antispam_Log**//"
                            "\n\n**GBanned User $SPOTTED**\n"
                            "**$SENRTY #CAS BAN**"
                            f"\n**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Razão:** `{reason}`\n**Ação Rápida:**"
                            f" Banido em {message.chat.title}\n\n$AUTOBAN #id{user_id}"
                        ),
                    )
        elif Config.SPAM_PROTECTION:
            try:
                iv = await get_response.json(
                    "https://api.intellivoid.net/spamprotection/v1/lookup?query="
                    + str(user_id)
                )
            except ValueError:
                pass
            else:
                if iv and (
                    iv["success"]
                    and iv["results"]["attributes"]["is_blacklisted"] is True
                ):
                    reason = iv["results"]["attributes"]["blacklist_reason"]
                    await asyncio.gather(
                        message.client.kick_chat_member(chat_id, user_id),
                        message.reply(
                            r"\\**#𝑿_Antispam**//"
                            "\n\nUsuário banido globalmente detectado neste bate-papo.\n\n"
                            "**$Intellivoid Spam Protection**"
                            f"\n**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Razão:** `{reason}`\n\n"
                            "**Ação Rápida:** Banido",
                            del_in=10,
                        ),
                        CHANNEL.log(
                            r"\\**#Antispam_Log**//"
                            "\n\n**GBanned User $SPOTTED**\n"
                            "**$Intellivoid Spam Protection**"
                            f"\n**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n**Quick Action:**"
                            f" Banned in {message.chat.title}\n\n$AUTOBAN #id{user_id}"
                        ),
                    )
        elif Config.SPAM_WATCH_API:
            try:
                intruder = await _get_spamwatch_data(user_id)
            except spamwatch.errors.Error as err:
                LOG.error(str(err))
            else:
                if intruder:
                    await asyncio.gather(
                        message.client.kick_chat_member(chat_id, user_id),
                        message.reply(
                            r"\\**#𝑿_Antispam**//"
                            "\n\nUsuário banido globalmente detectado neste bate-papo.\n\n"
                            "**$SENTRY SpamWatch Federation Ban**\n"
                            f"**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Razão:** `{intruder.reason}`\n\n"
                            "**Ação Rápida:** Banido",
                            del_in=10,
                        ),
                        CHANNEL.log(
                            r"\\**#Antispam_Log**//"
                            "\n\n**GBanned User $SPOTTED**\n"
                            "**$SENRTY #SPAMWATCH_API BAN**"
                            f"\n**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{intruder.reason}`\n"
                            f"**Ação Rápida:** Banido em {message.chat.title}\n\n"
                            f"$AUTOBAN #id{user_id}"
                        ),
                    )
    message.continue_propagation()


@pool.run_in_thread
def _get_spamwatch_data(user_id: int) -> Union[Ban, bool]:
    return spamwatch.Client(Config.SPAM_WATCH_API).get_ban(user_id)
