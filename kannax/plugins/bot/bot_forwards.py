# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

"""Encaminhamento de mensagens de bot"""

import asyncio
from math import floor
from time import time

from pyrogram import filters
from pyrogram.errors import (
    BadRequest,
    FloodWait,
    Forbidden,
    PeerIdInvalid,
    UserIsBlocked,
)

from kannax import Config, Message, get_collection, kannax
from kannax.utils import mention_html, time_formatter
from kannax.utils.extras import BotChat

LOG = kannax.getLogger(__name__)
CHANNEL = kannax.getCLogger(__name__)
BOT_BAN = get_collection("BOT_BAN")
BOT_START = get_collection("BOT_START")
SAVED_SETTINGS = get_collection("CONFIGS")
BOT_MSGS = BotChat("bot_forwards.csv")


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({"_id": "BOT_FORWARDS"})
    if data:
        Config.BOT_FORWARDS = bool(data["is_active"])


allowForwardFilter = filters.create(lambda _, __, ___: Config.BOT_FORWARDS)
ownersFilter = filters.user(list(Config.OWNER_ID))


@kannax.on_cmd(
    "bot_fwd", about={"header": "habilitar/desabilitar encaminhamento de mensagens"}, allow_channels=False
)
async def bot_fwd_(message: Message):
    """habilitar/desabilitar encaminhamento de mensagens"""
    if Config.BOT_FORWARDS:
        Config.BOT_FORWARDS = False
        await message.edit("`desabilitar encaminhamento de mensagens !`", del_in=3, log=__name__)
    else:
        Config.BOT_FORWARDS = True
        await message.edit("`habilitar encaminhamento de mensagens !`", del_in=3, log=__name__)
    await SAVED_SETTINGS.update_one(
        {"_id": "BOT_FORWARDS"},
        {"$set": {"is_active": Config.BOT_FORWARDS}},
        upsert=True,
    )


if kannax.has_bot:

    @kannax.bot.on_message(
        allowForwardFilter
        & ~ownersFilter
        & filters.private
        & filters.incoming
        & ~filters.command("start")
    )
    async def forward_bot(_, message: Message):
        try:
            msg = await message.forward(Config.OWNER_ID[0])
        except UserIsBlocked:
            await CHANNEL.log("**ERROR**: You Blocked your Bot !")
        except Exception as new_m_e:
            await CHANNEL.log(
                f"Não posso enviar mensagem para __ID__: {Config.OWNER_ID[0]}"
                "\n**Nota:** a mensagem será enviada para o primeiro id em `OWNER_ID` ape!"
                f"\n\n**ERROR:** `{new_m_e}`"
            )
        else:
            BOT_MSGS.store(msg.message_id, message.from_user.id)

    @kannax.bot.on_message(
        allowForwardFilter
        & filters.user(Config.OWNER_ID[0])
        & filters.private
        & filters.reply
        & ~filters.regex(
            pattern=f"^(/.+|\{Config.SUDO_TRIGGER}(spoiler|cbutton)\s(.+)?)"
        ),
    )
    async def forward_reply(_, message: Message):
        reply = message.reply_to_message
        to_copy = not message.poll
        user_fwd = reply.forward_from
        if user_fwd:
            # Incase message is your own forward
            if user_fwd.id in Config.OWNER_ID:
                return
            user_id = user_fwd.id
        else:
            if not reply.forward_sender_name:
                return
            if not (user_id := BOT_MSGS.search(reply.message_id)):
                await kannax.bot.send_message(
                    Config.OWNER_ID[0],
                    "`You can't reply to old messages with if user's"
                    "forward privacy is enabled`",
                    del_in=5,
                )
                return
        try:
            if to_copy:
                await message.copy(user_id)
            else:
                await message.forward(user_id)
        except UserIsBlocked:
            await message.err(
                "Você não pode responder a este usuário porque ele bloqueou seu bot !", del_in=5
            )
        except Exception as fwd_e:
            LOG.error(fwd_e)

    @kannax.bot.on_message(
        filters.user(Config.OWNER_ID[0])
        & filters.private
        & filters.incoming
        & filters.regex(pattern=r"^/ban\s+(.*)")
    )
    async def bot_ban_(_, message: Message):
        """banir um usuário do bot"""
        start_ban = await kannax.bot.send_message(message.chat.id, "`Banindo")
        user_id, reason = extract_content(message)  # Ban by giving ID & Reason
        if not user_id:
            await start_ban.err("ID do usuário não encontrado", del_in=10)
            return
        if not reason:
            await message.err("Ban abortado! forneça uma razão primeiro!")
            return
        ban_user = await kannax.bot.get_user_dict(user_id, attr_dict=True)
        if ban_user.id in Config.OWNER_ID:
            await start_ban.edit("Eu não posso te banir voce é meu mestre")
            return
        if ban_user.id in Config.SUDO_USERS:
            await start_ban.edit(
                "Esse usuário está em minha lista de Sudo,"
                "Portanto, não posso bani-lo do bot\n"
                "\n**Nota:** Remova-os da Lista de Sudo e tente novamente.",
                del_in=5,
            )
            return
        if found := await BOT_BAN.find_one({"user_id": ban_user.id}):
            await start_ban.edit(
                "**#Already_Banned_from_Bot_PM**\n\n"
                "O usuário já existe na lista de BAN do meu bot.\n"
                f"**Motivo do BAN:** `{found.get('reason')}`",
                del_in=5,
            )
        else:
            await start_ban.edit(await ban_from_bot_pm(ban_user, reason), log=__name__)

    async def ban_from_bot_pm(ban_user, reason: str, log: str = False) -> None:
        user_ = await kannax.bot.get_user_dict(ban_user, attr_dict=True)
        banned_msg = (
            f"<i>**Você foi banido para sempre**" f"</i>\n**Motivo** : {reason}"
        )
        await asyncio.gather(
            BOT_BAN.insert_one(
                {"firstname": user_.fname, "user_id": user_.id, "reason": reason}
            ),
            kannax.bot.send_message(user_.id, banned_msg),
        )
        info = (
            r"\\**#Banned_Bot_PM_User**//"
            f"\n\n👤 {user_.mention}\n"
            f"**Primeiro Nome:** {user_.fname}\n"
            f"**User ID:** `{user_.id}`\n**Reason:** `{reason}`"
        )
        if log:
            await kannax.getCLogger(log).log(info)
        return info

    @kannax.bot.on_message(
        allowForwardFilter
        & filters.user(list(Config.OWNER_ID))
        & filters.private
        & filters.command("broadcast")
    )
    async def broadcast_(_, message: Message):
        replied = message.reply_to_message
        if not replied:
            await message.reply("Responda a uma mensagem para Broadcasting primeiro !")
            return
        start_ = time()
        br_cast = await replied.reply("Broadcasting ...")
        blocked_users = []
        count = 0
        to_copy = not replied.poll
        bot_users_count = await BOT_START.estimated_document_count()
        async for c in BOT_START.find():
            try:
                b_id = c["user_id"]
                if b_id in Config.OWNER_ID:
                    await BOT_START.find_one_and_delete({"user_id": b_id})
                else:
                    await kannax.bot.send_message(
                        b_id, "🔊 Você recebeu um **novo** Broadcast."
                    )
                    if to_copy:
                        await replied.copy(b_id)
                    else:
                        await replied.forward(b_id)
                    await asyncio.sleep(0.8)
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except (BadRequest, Forbidden):
                blocked_users.append(
                    BOT_START.find_one_and_delete({"user_id": b_id})
                )  # coro list of removing users
            except Exception as err:
                await CHANNEL.log(str(err))
            else:
                count += 1
                if count % 5 == 0:
                    try:
                        prog_ = (
                            "🔊 Broadcasting ...\n\n"
                            + progress_str(
                                total=bot_users_count,
                                current=count + len(blocked_users),
                            )
                            + f"\n\n• ✔️ **Sucesso** :  `{count}`\n"
                            + f"• ✖️ **Fail** :  `{len(blocked_users)}`"
                        )
                        await br_cast.edit(prog_)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
        end_ = time()
        b_info = f"🔊  Mensagem transmitida com sucesso para ➜  <b>{count} users.</b>"
        if len(blocked_users) != 0:
            b_info += f"\n🚫  <b>{len(blocked_users)} users</b> bloqueou seu bot recentemente, então foi removido."
        b_info += f"\n⏳  <code>Processo levou: {time_formatter(end_ - start_)}</code>."
        await br_cast.edit(b_info, log=__name__)
        if blocked_users:
            await asyncio.gather(*blocked_users)

    @kannax.bot.on_message(
        filters.user(Config.OWNER_ID[0])
        & filters.private
        & filters.reply
        & filters.command("uinfo")
    )
    async def uinfo_(_, message: Message):
        reply = message.reply_to_message
        user_ = None
        if not reply:
            await message.reply("Responda a uma mensagem para ver as informações do usuário")
            return
        info_msg = await message.reply("`🔎 Procurando este usuário em meu banco de dados ...`")
        if uid_from_db := BOT_MSGS.search(reply.message_id):
            try:
                user_ = await kannax.bot.get_user_dict(uid_from_db, attr_dict=True)
            except Exception:
                pass
        elif user_from_fwd := reply.forward_from:
            user_ = await kannax.bot.get_user_dict(user_from_fwd, attr_dict=True)

        if not user_:
            return await message.edit(
                "**ERROR:** `Desculpe! Não consigo encontrar este usuário em meu banco de dados :(`", del_in=3
            )
        uinfo = (
            "**#User_Info**"
            f"\n\n👤 {user_.mention}\n"
            f"**Primeiro Nome:** {user_.fname}\n"
            f"**User ID:** `{user_.id}`"
        )
        await info_msg.edit(uinfo)


def extract_content(msg: Message):  # Modified a bound method
    id_reason = msg.matches[0].group(1)
    replied = msg.reply_to_message
    user_id, reason = None, None
    if replied:
        fwd = replied.forward_from
        if fwd and id_reason:
            user_id = fwd.id
            reason = id_reason
        if replied.forward_sender_name and id_reason:
            reason = id_reason
            user_id = BOT_MSGS.search(replied.message_id)
    else:
        if id_reason:
            data = id_reason.split(maxsplit=1)
            # Grab First Word and Process it.
            if len(data) == 2:
                user, reason = data
            elif len(data) == 1:
                user = data[0]
            # if user id, convert it to integer
            if user.isdigit():
                user_id = int(user)
            # User @ Mention.
            if user.startswith("@"):
                user_id = user
    return user_id, reason


@kannax.on_cmd(
    "bblist",
    about={
        "header": "Obtenha uma lista de usuários banidos por bot",
        "description": "Obtenha uma lista atualizada de usuários que foram banidos por você.",
        "examples": "{tr}bblist",
    },
    allow_channels=False,
)
async def list_bot_banned(message: Message):
    """visualizar usuários do bot banidos"""
    msg = ""
    async for c in BOT_BAN.find():
        msg += (
            "**Usuario** : "
            + str(c["firstname"])
            + "-> with **User ID** -> "
            + str(c["user_id"])
            + " is **Bot Banned for** : "
            + str(c["reason"])
            + "\n\n"
        )

    await message.edit_or_send_as_file(
        f"**--Lista de usuários banidos do bot--**\n\n{msg}" if msg else "`bblist vazia!`"
    )


@kannax.on_cmd(
    "unbban",
    about={
        "header": "Desbanir um usuário do bot",
        "description": "Remove um usuário da sua lista de ban",
        "examples": "{tr}unbban [userid]",
    },
    allow_channels=False,
    allow_bots=True,
)
async def ungban_user(message: Message):
    """desbanir um usuário do PM do Bot"""
    await message.edit("`UN-BOT Banning ...`")
    user_id = message.input_str
    if not user_id:
        await message.err("Nenhuma entrada encontrada !")
        return
    user_id = message.input_str.split()[0].strip()
    try:
        get_mem = await message.client.get_user_dict(user_id)
    except (PeerIdInvalid, IndexError):
        firstname = "Não conhecido !"
        if user_id.isdigit():
            user_id = int(user_id)
        else:
            await message.err("Usuário desconhecido!, Forneça uma ID de usuário para pesquisar.")
            return
    else:
        firstname = get_mem["fname"]
        user_id = get_mem["id"]
    found = await BOT_BAN.find_one({"user_id": user_id})
    if not found:
        await message.err("Usuário não encontrado na lista de banimento do meu bot")
        return
    await asyncio.gather(
        BOT_BAN.delete_one(found),
        message.edit(
            r"\\**#Bot_UnBanned_User**//"
            f"\n\n  **Primeiro Nome:** {mention_html(user_id, firstname)}"
            f"\n  **User ID:** `{user_id}`"
        ),
    )


@kannax.on_cmd(
    "bot_forwards", about={"header": "Ajuda sobre comandos para encaminhamentos de bot"}
)
async def bf_help(message: Message):
    """Veja isto para obter ajuda"""
    cmd_ = Config.CMD_TRIGGER
    bot_forwards_help = f"""
        **Comandos Disponíveis**

    [Toggle]
• `{cmd_}bot_fwd` - Ativar / Desativar encaminhamentos de bot

    <i>funciona **apenas em** bot pm</i>
• `/ban` - Banir um usuário do bot PM
    e.g-
    /ban [responder a mensagem encaminhada com o motivo]
    /ban [user_id/user_name] motivo

• `/broadcast` - Envie uma mensagem de broadcast para os usuários em seu `{cmd_}bot_users`
    e.g-
    /broadcast [responda a uma mensagem]

• `/uinfo` - Obter informações do usuário
    e.g-
    /uinfo [responder a mensagem encaminhada]

    <i>pode usar fora do bot pm</i>
• `{cmd_}bblist` - BotBanList (Usuários banidos do PM do seu bot)
    e.g-
    {cmd_}bblist

• `{cmd_}unbban` - UnBotBan  (Desbanir usuários que estão em BotBanList)
    e.g-
    {cmd_}unbban [user_id/user_name]
    Hint: Verifique o bblist para usuários banidos.
"""
    await message.edit(bot_forwards_help, del_in=60)


def progress_str(total: int, current: int) -> str:
    percentage = current * 100 / total
    prog_arg = "**Progresso** : `{}%`\n" "```[{}{}]```"
    return prog_arg.format(
        percentage,
        "".join((Config.FINISHED_PROGRESS_STR for i in range(floor(percentage / 5)))),
        "".join(
            (Config.UNFINISHED_PROGRESS_STR for i in range(20 - floor(percentage / 5)))
        ),
    )
