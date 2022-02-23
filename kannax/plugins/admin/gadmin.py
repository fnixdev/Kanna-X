""" gerencie seu grupo """

import asyncio
import os
import time

from pyrogram.errors import (
    FloodWait,
    PeerIdInvalid,
    UserAdminInvalid,
    UserIdInvalid,
    UsernameInvalid,
)
from pyrogram.methods.chats import delete_channel
from pyrogram.types import ChatPermissions

from kannax import Config, Message, kannax
from kannax.utils.functions import get_emoji_regex
from kannax.utils import is_dev

CHANNEL = kannax.getCLogger(__name__)


@kannax.on_cmd(
    "banc",
    about={
        "header": "use isso para banir canais do grupo",
        "description": "Responda a mensagem de um canal para bani-lo",
    },
    allow_channels=False,
    check_restrict_perm=True,
)
async def ban_user(message: Message):
    await message.edit("`Tentando banir o canal !!`")
    chat_id = message.chat.id
    id_ = message.extract_sender
    if id_ == False:
        return await message.edit("`Você precisa responder a mensagem de um canal.`")
    try:
        await message.client.ban_chat_member(chat_id, id_)
        await message.edit("`Canal banido com sucesso.`")
    except PeerIdInvalid:
        await message.edit(
                    "`ID de canal inválido, tente novamente com informações válidas.`", del_in=5
                )
    except Exception as e_f:
        await message.edit(
                    "`Algo deu errado 🤔, .help unbanc para mais informações`\n\n"
                    f"**ERROR**: `{e_f}`",
                    del_in=5,
                )


@kannax.on_cmd(
    "unbanc",
    about={
        "header": "use isso para desbanir canais do grupo",
        "description": "Responda a mensagem de um canal para desbani-lo",
    },
    allow_channels=False,
    check_restrict_perm=True,
)
async def ban_user(message: Message):
    await message.edit("`Tentando desbanir o canal !!`")
    chat_id = message.chat.id
    id_ = message.extract_sender
    if id_ == False:
        return await message.edit("`Você precisa responder a mensagem de um canal.`")
    try:
        await message.client.unban_chat_member(chat_id, id_)
        await message.edit("`Canal desbanido com sucesso.`")
    except PeerIdInvalid:
        await message.edit(
            "`ID de canal inválido, tente novamente com informações válidas.`", del_in=5
        )
    except Exception as e_f:
        await message.edit(
            "`Algo deu errado 🤔, .help unbanc para mais informações`\n\n"
            f"**ERROR**: `{e_f}`",
            del_in=5,
        )


@kannax.on_cmd(
    "promote",
    about={
        "header": "use isso para promover os membros do grupo",
        "description": "Concede direitos de administrador para a pessoa no grupo.\n"
        "você também pode adicionar um título personalizado enquanto promove um novo administrador.\n"
        "[NOTA: Requer direitos de administrador adequados no chat!!!]",
        "examples": [
            "{tr}promote [username | userid] ou [responda um user] :título personalizado (opcional)",
        ],
    },
    allow_channels=False,
    check_promote_perm=True,
)
async def promote_usr(message: Message):
    """promote members in tg group"""
    chat_id = message.chat.id
    await message.edit("`Tentando promover o usuário .. Espere aí!! ⏳`")
    user_id, custom_rank = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`nenhum user_id válido ou mensagem especificada,`"
            "`.help promote para mais informações`",
            del_in=5,
        )
        return
    if custom_rank:
        custom_rank = get_emoji_regex().sub("", custom_rank)
        if len(custom_rank) > 15:
            custom_rank = custom_rank[:15]
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        await message.client.promote_chat_member(
            chat_id,
            user_id,
            can_change_info=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
        )
        if custom_rank:
            await asyncio.sleep(2)
            await message.client.set_administrator_title(chat_id, user_id, custom_rank)
        await message.edit("`👑 Promovido com sucesso..`", del_in=5)
        await CHANNEL.log(
            "#PROMOTE\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CUSTOM TITLE: `{custom_rank or None}`\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)"
        )
    except UsernameInvalid:
        await message.edit("`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit(
            "`nome de usuário ou ID de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
        )
    except UserIdInvalid:
        await message.edit("`ID de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(f"`algo deu errado! 🤔`\n\n**ERROR:** `{e_f}`")


@kannax.on_cmd(
    "demote",
    about={
        "header": "use isso para rebaixar membros do grupo",
        "description": "Remova os direitos de administrador do usuario no grupo.\n"
        "[NOTA: Requer direitos de administrador adequados no chat!!!]",
        "examples": "{tr}demote [username | userid] ou [responda um user]",
    },
    allow_channels=False,
    check_promote_perm=True,
)
async def demote_usr(message: Message):
    """demote members in tg group"""
    chat_id = message.chat.id
    await message.edit("`Tentando rebaixar o usuário .. Espere aí!! ⏳`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`nenhum user_id válido ou mensagem especificada,`"
            "`.help demote para mais informações` ⚠",
            del_in=5,
        )
        return
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        await message.client.promote_chat_member(
            chat_id,
            user_id,
            can_change_info=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_invite_users=False,
            can_pin_messages=False,
        )
        await message.edit("`🛡 Rebaixado com sucesso..`", del_in=5)
        await CHANNEL.log(
            "#DEMOTE\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)"
        )
    except UsernameInvalid:
        await message.edit("`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit(
            "`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
        )
    except UserIdInvalid:
        await message.edit("`ID de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(f"`algo deu errado! 🤔`\n\n**ERROR:** `{e_f}`", del_in=5)



@kannax.on_cmd(
    "ban",
    about={
        "header": "use isso para banir membros do grupo",
        "description": "Banir membro do grupo.\n"
        "[NOTA: Requer direitos de administrador adequados no chat!!!]",
        "flags": {"-m": "minutos", "-h": "horas", "-d": "dias"},
        "examples": "{tr}ban [flag] [username | userid] ou [respnde um user] :motivo (opcional)",
    },
    allow_channels=False,
    check_restrict_perm=True,
)
async def ban_user(message: Message):
    """ban user from tg group"""
    await message.edit("`Tentando banir o usuário .. Espere aí!! ⏳`")
    user_id, reason = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`nenhum user_id válido ou mensagem especificada,`"
            "`.help ban para mais informações`",
            del_in=5,
        )
        return
    chat_id = message.chat.id
    flags = message.flags
    minutes = int(flags.get("-m", 0))
    hours = int(flags.get("-h", 0))
    days = int(flags.get("-d", 0))

    ban_period = 0
    _time = "forever"
    if minutes:
        ban_period = time.time() + minutes * 60
        _time = f"{minutes}m"
    elif hours:
        ban_period = time.time() + hours * 3600
        _time = f"{hours}h"
    elif days:
        ban_period = time.time() + days * 86400
        _time = f"{days}d"
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        if is_dev(get_mem.user.id):
            return await message.edit("`Lol ele é meu desenvolvedor porque iria bani-lo?.`")
        await message.reply_sticker("CAACAgEAAx0CSqdu1wACKuZhVF4AASJoh-uceGFGliKa5mRjEZgAAmQBAAKoqYlG7o7Z_jOv9AQeBA")
        await asyncio.sleep(2)
        await message.client.ban_chat_member(chat_id, user_id, int(ban_period))
        await message.edit(
            "#BAN\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
            f"TIME: `{_time}`\n"
            f"REASON: `{reason}`",
            log=__name__,
        )
    except UsernameInvalid:
        await message.edit("`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit(
            "`nome de usuário ou ID de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
        )
    except UserIdInvalid:
        await message.edit("`ID de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(
            "`algo deu errado 🤔, .help ban para mais informações`\n\n"
            f"**ERROR**: `{e_f}`",
            del_in=5,
        )


@kannax.on_cmd(
    "unban",
    about={
        "header": "use isso para cancelar o banimento de membros do grupo",
        "description": "Desbanir membro do grupo.\n"
        "[NOTA: Requer direitos de administrador adequados no chat!!!]",
        "examples": "{tr}unban [username | userid] ou [responda um user]",
    },
    allow_channels=False,
    check_restrict_perm=True,
)
async def unban_usr(message: Message):
    """unban user from tg group"""
    chat_id = message.chat.id
    await message.edit("`Tentando desbanir usuário .. Espere aí!! ⏳`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`nenhum user_id ou mensagem válida especificada,`"
            "`.help unban para mais informações` ⚠",
            del_in=5,
        )
        return
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        await message.client.unban_chat_member(chat_id, user_id)
        await message.edit("`🛡 Desbanido com suceso..`", del_in=5)
        await CHANNEL.log(
            "#UNBAN\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)"
        )
    except UsernameInvalid:
        await message.edit("`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit(
            "`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
        )
    except UserIdInvalid:
        await message.edit("`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(f"`algo deu errado! 🤔`\n\n**ERROR:** `{e_f}`", del_in=5)


@kannax.on_cmd(
    "kick",
    about={
        "header": "use isso para kickar membros do grupo",
    },
    allow_channels=False,
    check_restrict_perm=True,
)
async def kick_usr(message: Message):
    """kick user from tg group"""
    chat_id = message.chat.id
    await message.edit("`Tentando chutar o usuário .. Espere aí!! ⏳`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`nenhum user_id ou mensagem válida especificada,`"
            "`.help kick para mais informações` ⚠",
            del_in=5,
        )
        return
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        if is_dev(get_mem.user.id):
            await message.edit("`Lol ele é meu desenvolvedor porque iria expulsa-lo?.`")
            return
        await message.client.ban_chat_member(chat_id, user_id, int(time.time() + 60))
        await message.edit(
            "#KICK\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)",
            log=__name__,
        )
    except UsernameInvalid:
        await message.edit("`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit(
            "`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
        )
    except UserIdInvalid:
        await message.edit("`ID de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(f"`algo deu errado! 🤔`\n\n**ERROR:** `{e_f}`", del_in=5)


@kannax.on_cmd(
    "kickme",
    about={
        "header": "saia do chat",
        "description": "faz com que você saia do chat rapidamente."
    },
    allow_channels=False,
)
async def kickme_chat(message: Message):
    """leave chat"""
    chat_id = message.chat.id
    await message.delete()
    await message.client.leave_chat(chat_id)


@kannax.on_cmd(
    "mute",
    about={
        "header": "use isso para mutar membros do grupo",
        "flags": {"-m": "minutos", "-h": "horas", "-d": "dias"},
    },
    allow_channels=False,
    check_restrict_perm=True,
)
async def mute_usr(message: Message):
    """mute user from tg group"""
    chat_id = message.chat.id
    flags = message.flags
    minutes = flags.get("-m", 0)
    hours = flags.get("-h", 0)
    days = flags.get("-d", 0)
    await message.edit("`Tentando mutar o usuário .. Espere aí!! ⏳`")
    user_id, reason = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`nenhum user_id ou mensagem válida especificada,`"
            "`.help mute para mais informações`",
            del_in=5,
        )
        return
    if minutes:
        mute_period = int(minutes) * 60
        _time = f"{int(minutes)}m"
    elif hours:
        mute_period = int(hours) * 3600
        _time = f"{int(hours)}h"
    elif days:
        mute_period = int(days) * 86400
        _time = f"{int(days)}d"
    if flags:
        try:
            get_mem = await message.client.get_chat_member(chat_id, user_id)
            if is_dev(get_mem.user.id):
                return await message.reply("`Lol ele é meu desenvolvedor porque iria muta-lo?.`")
            await message.client.restrict_chat_member(
                chat_id, user_id, ChatPermissions(), int(time.time() + mute_period)
            )
            await message.edit(
                "#MUTE\n\n"
                f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                f"(`{get_mem.user.id}`)\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"MUTE UNTIL: `{_time}`\n"
                f"REASON: `{reason}`",
                log=__name__,
            )
        except UsernameInvalid:
            await message.edit(
                "`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
            )
        except PeerIdInvalid:
            await message.edit(
                "`nome de usuário ou ID de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
            )
        except UserIdInvalid:
            await message.edit(
                "`ID de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
            )
        except Exception as e_f:
            await message.edit(
                "`algo deu errado! 🤔, .help mute para mais informações`\n\n"
                f"**ERROR**: `{e_f}`",
                del_in=5,
            )
    else:
        try:
            get_mem = await message.client.get_chat_member(chat_id, user_id)
            await message.client.restrict_chat_member(
                chat_id, user_id, ChatPermissions()
            )
            await message.edit(
                "#MUTE\n\n"
                f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                f"(`{get_mem.user.id}`)\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"MUTE UNTIL: `forever`\n"
                f"REASON: `{reason}`",
                log=__name__,
            )
        except UsernameInvalid:
            await message.edit(
                "`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
            )
        except PeerIdInvalid:
            await message.edit(
                "`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
            )
        except UserIdInvalid:
            await message.edit(
                "`ID de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5
            )
        except Exception as e_f:
            await message.edit(
                "`algo deu errado! 🤔, .help mute para mais informações`\n\n"
                f"**ERROR**: {e_f}",
                del_in=5,
            )


@kannax.on_cmd(
    "unmute",
    about={
        "header": "use isso para desmutar membros do grupo",
    },
    allow_channels=False,
    check_restrict_perm=True,
)
async def unmute_usr(message: Message):
    """unmute user from tg group"""
    chat_id = message.chat.id
    await message.edit("`Tentando mutar o usuário .. Espere aí!! ⏳`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`nenhum user_id ou mensagem válida especificada,`"
            "`.help unmute para mais informações`",
            del_in=5,
        )
        return
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        await message.client.unban_chat_member(chat_id, user_id)
        await message.edit("`🛡 Desmutado com Sucesso..`", del_in=5)
        await CHANNEL.log(
            "#UNMUTE\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)"
        )
    except UsernameInvalid:
        await message.edit("`nome de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit(
            "`invalid username or userid, try again with valid info ⚠`", del_in=5
        )
    except UserIdInvalid:
        await message.edit("`ID de usuário inválido, tente novamente com informações válidas ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(f"`algo deu errado!` 🤔\n\n**ERROR:** `{e_f}`", del_in=5)


@kannax.on_cmd(
    "zombies",
    about={
        "header": "use isso para limpar contas de zumbis",
        "description": "verificar e remover contas zumbis (excluídas) do grupo.",
        "flags": {"-c": "clean"},
        "examples": [
            "{tr}zombies [verificar contas excluídas no grupo]",
            "{tr}zombies -c [remover contas excluídas do grupo]",
        ],
    },
    allow_channels=False,
    allow_bots=False,
    allow_private=False,
)
async def zombie_clean(message: Message):
    """remove deleted accounts from tg group"""
    chat_id = message.chat.id
    flags = message.flags
    rm_delaccs = "-c" in flags
    can_clean = bool(
        not message.from_user
        or message.from_user
        and (
            await message.client.get_chat_member(message.chat.id, message.from_user.id)
        ).status
        in ("administrator", "creator")
    )
    if rm_delaccs:
        del_users = 0
        del_admins = 0
        del_total = 0
        del_stats = r"`Zero zombie accounts found in this chat... WOOHOO group is clean.. \^o^/`"
        if can_clean:
            await message.edit("`Espere!! limpando contas de zumbis deste bate-papo..`")
            async for member in message.client.iter_chat_members(chat_id):
                if member.user.is_deleted:
                    try:
                        await message.client.ban_chat_member(
                            chat_id, member.user.id, int(time.time() + 45)
                        )
                    except UserAdminInvalid:
                        del_users -= 1
                        del_admins += 1
                    except FloodWait as e_f:
                        time.sleep(e_f.x)
                    del_users += 1
                    del_total += 1
            if del_admins > 0:
                del_stats = f"`👻 Foi encontrado` **{del_total}** `zumbis..`\
                \n`🗑 Removidos` **{del_users}** `zumbis..`\
                \n🛡 **{del_admins}** `deleted admin accounts are skipped!!`"
            else:
                del_stats = f"`👻 Foi encontrado` **{del_total}** `zumbis..`\
                \n`🗑 Removidos` **{del_users}** `zumbis..`"
            await message.edit(f"{del_stats}", del_in=5)
            await CHANNEL.log(
                "#ZOMBIE_CLEAN\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"TOTAL ZOMBIE COUNT: `{del_total}`\n"
                f"CLEANED ZOMBIE COUNT: `{del_users}`\n"
                f"ZOMBIE ADMIN COUNT: `{del_admins}`"
            )
        else:
            await message.edit(
                r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=5
            )
    else:
        del_users = 0
        del_stats = r"`Zero zombie accounts found in this chat... WOOHOO group is clean.. \^o^/`"
        await message.edit("`🔎 Procurando contas de zumbis neste bate-papo..`")
        async for member in message.client.iter_chat_members(chat_id):
            if member.user.is_deleted:
                del_users += 1
        if del_users > 0:
            del_stats = f"`Encontrado` **{del_users}** `contas zumbis neste chat.`"
            await message.edit(
                f"🕵️‍♂️ {del_stats} you can clean them using `{Config.CMD_TRIGGER}zombies -c`",
                del_in=5,
            )
            await CHANNEL.log(
                "#ZOMBIE_CHECK\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"ZOMBIE COUNT: `{del_users}`"
            )
        else:
            await message.edit(f"{del_stats}", del_in=5)
            await CHANNEL.log(
                "#ZOMBIE_CHECK\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                r"ZOMBIE COUNT: `WOOHOO group is clean.. \^o^/`"
            )


def chat_name_(msg: Message):
    chat_ = msg.chat
    if chat_.type in ("private", "bot"):
        return " ".join([chat_.first_name, chat_.last_name or ""])
    return chat_.title


@kannax.on_cmd(
    "unpin",
    about={
        "header": "use para desfixar mensagens",
        "flags": {"-all": "desfixa todas as mensagens"},
        "examples": [
            "{tr}unpin [responda uma mensagem]",
            "{tr}unpin -all [responda uma mensagem no chat]",
        ],
    },
    check_pin_perm=True,
)
async def unpin_msgs(message: Message):
    """unpin message"""
    reply = message.reply_to_message
    unpinall_ = bool("-all" in message.flags)
    try:
        if unpinall_:
            await message.client.unpin_all_chat_messages(message.chat.id)
        else:
            if not reply:
                await message.err("Primeiro responda uma mensagem para desfixar !", del_in=5)
                return
            await reply.unpin()
        await message.delete()
        await CHANNEL.log(
            f"{'#UNPIN_All' if unpinall_ else '#UNPIN'}\n\nCHAT: **{chat_name_(message)}**  (`{message.chat.id}`)"
        )
    except Exception as e_f:
        await message.err(e_f + "\n.help unpin para informações ...", del_in=7)


@kannax.on_cmd(
    "pin",
    about={
        "header": "use para fixar mensagens",
        "description": "fixa mensagens no grupo, com ou sem aviso aos usuarios.",
        "flags": {
            "-s": "silent",
            "-me": "apenas para voçê (para chat privado apenas)",
        },
        "examples": [
            "{tr}pin [responda a uma mensagem]",
            "{tr}pin -s [responda a uma mensagem]",
            "{tr}pin -me [envie para o chat privado]",
        ],
    },
    check_pin_perm=True,
)
async def pin_msgs(message: Message):
    """pin message"""
    reply = message.reply_to_message
    if not reply:
        await message.err("Primeiro responda uma mensagem para fixar !", del_in=5)
        return
    try:
        await reply.pin(
            disable_notification=bool("-s" in message.flags),
            both_sides=(not bool("-me" in message.flags)),
        )
        await message.delete()
        await CHANNEL.log(
            f"#PIN\n\nCHAT: **{chat_name_(message)}**  (`{message.chat.id}`)"
        )
    except Exception as e_f:
        await message.err(e_f + "\n.help pin para informações ...", del_in=7)


@kannax.on_cmd(
    "smode",
    about={
        "header": "ligar/desligar o modo lento de bate-papo",
        "description": "use isso para desligar ou alternar entre o modo lento de bate-papo \n"
        "disponiveis 6 modos, s10/s30/m1/m5/m15/h1",
        "flags": {"-s": "segundos", "-m": "minutos", "-h": "horas", "-o": "off"},
        "types": [
            "-s10 = 10 segundos",
            "-s30 = 30 segundos",
            "-m1 = 1 minutos",
            "-m5 = 5 minutos",
            "-m15 = 15 minutos",
            "-h1 = 1 hora",
        ],
        "examples": [
            "{tr}smode -s30 [envie no chat] (ligar o modo 30s lento) ",
            "{tr}smode -o [send to chat] (desligar o modo lento)",
        ],
    },
    allow_channels=False,
    check_promote_perm=True,
)
async def smode_switch(message: Message):
    """turn on/off chat slow mode"""
    chat_id = message.chat.id
    flags = message.flags
    seconds = flags.get("-s", 0)
    minutes = flags.get("-m", 0)
    hours = flags.get("-h", 0)
    smode_off = "-o" in flags
    if seconds:
        try:
            seconds = int(seconds)
            await message.client.set_slow_mode(chat_id, seconds)
            await message.edit(
                f"`⏳ ligado o modo lento por {seconds} segundos no bate-papo!`", del_in=5
            )
            await CHANNEL.log(
                f"#SLOW_MODE\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"SLOW MODE TIME: `{seconds} segundos`"
            )
        except Exception as e_f:
            await message.edit(
                "`algo deu errado!!, use .help smode para informações..` \n\n"
                f"**ERROR:** `{e_f}`"
            )
    elif minutes:
        try:
            smode_time = int(minutes) * 60
            await message.client.set_slow_mode(chat_id, smode_time)
            await message.edit(
                f"`⏳ ligado o modo lento por {minutes} minutos no bate-papo!`", del_in=5
            )
            await CHANNEL.log(
                f"#SLOW_MODE\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"SLOW MODE TIME: `{minutes} minutos`"
            )
        except Exception as e_f:
            await message.edit(
                "`algo deu errado!!, use .help smode para informações..` \n\n"
                f"**ERROR:** `{e_f}`"
            )
    elif hours:
        try:
            smode_time = int(hours) * 3600
            await message.client.set_slow_mode(chat_id, smode_time)
            await message.edit("`⏳ ligado o modo lento por 1 hora no chat!`", del_in=5)
            await CHANNEL.log(
                f"#SLOW_MODE\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"SLOW MODE TIME: `{hours} hours`"
            )
        except Exception as e_f:
            await message.edit(
                "`algo deu errado!!, use .help smode para informações..` \n\n"
                f"**ERROR:** `{e_f}`"
            )
    elif smode_off:
        try:
            await message.client.set_slow_mode(chat_id, 0)
            await message.edit("`⏳ desligado modo lento no chat!`", del_in=5)
            await CHANNEL.log(
                f"#SLOW_MODE\n\nCHAT: `{message.chat.title}` (`{chat_id}`)\nSLOW MODE: `Off`"
            )
        except Exception as e_f:
            await message.edit(
                f"`algo deu errado!!, use .help smode para informações..` \n\n**ERROR:** `{e_f}`"
            )
    else:
        await message.edit(
            "`flag type/mode inválido.. use .help smode para informações!!`", del_in=5
        )
