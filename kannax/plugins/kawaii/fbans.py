"""Plugin para gerenciar federações"""
# Author: Copyright (C) 2020 KenHV [https://github.com/KenHV]

# For KannaX
# Ported to Pyrogram + Rewrite with Mongo DB
# by: (TG - @DeletedUser420) [https://github.com/code-rgb]
# Thanks @Lostb053  for writing help
import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait, Forbidden, PeerIdInvalid

from kannax import Config, Message, get_collection, kannax

FED_LIST = get_collection("FED_LIST")
CHANNEL = kannax.getCLogger(__name__)


@kannax.on_cmd(
    "addf",
    about={
        "header": "Adicionar um bate-papo à lista do Fed",
        "description": "Adicionar um bate-papo à lista de feeds onde a mensagem deve ser enviada",
        "usage": "{tr}addf",
    },
    allow_bots=False,
    allow_channels=False,
    allow_private=False,
)
async def addfed_(message: Message):
    """Adiciona bate-papo atual aos federais conectados."""
    name = message.input_str or message.chat.title
    chat_id = message.chat.id
    found = await FED_LIST.find_one({"chat_id": chat_id})
    if found:
        await message.edit(
            f"Chat __ID__: `{chat_id}`\nFed: **{found['fed_name']}**\n\nJá existe na Lista Fed !",
            del_in=7,
        )
        return
    await FED_LIST.insert_one({"fed_name": name, "chat_id": chat_id})
    msg_ = f"__ID__ `{chat_id}` adicionado a Fed: **{name}**"
    await message.edit(msg_, log=__name__, del_in=7)


@kannax.on_cmd(
    "delf",
    about={
        "header": "Remover um bate-papo da lista de fed",
        "flags": {"-all": "Remova todas as feds do fedlist"},
        "description": "Remover um bate-papo da lista de feds",
        "usage": "{tr}delf",
    },
    allow_bots=False,
    allow_channels=False,
    allow_private=False,
)
async def delfed_(message: Message):
    """Remove o bate-papo atual das defs conectados."""
    if "-all" in message.flags:
        msg_ = "**Desconectado de todas as feds conectadas!**"
        await message.edit(msg_, log=__name__, del_in=7)
        await FED_LIST.drop()
    else:
        try:
            chat_ = await message.client.get_chat(message.input_str or message.chat.id)
        except (PeerIdInvalid, IndexError):
            return await message.err("Forneça um ID de bate-papo válido", del_in=7)
        chat_id = chat_.id
        out = f"{chat_.title}\nChat ID: {chat_id}\n"
        found = await FED_LIST.find_one({"chat_id": chat_id})
        if found:
            msg_ = out + f"Fed removida com sucesso: **{found['fed_name']}**"
            await message.edit(msg_, log=__name__, del_in=7)
            await FED_LIST.delete_one(found)
        else:
            return await message.err(
                out + "**Não existe na sua Lista Fed !**", del_in=7
            )


@kannax.on_cmd(
    "fban",
    about={
        "header": "Fban user",
        "description": "Fban o usuário da lista de feds",
        "usage": "{tr}fban [username|responder o usuario|user_id] [razão (opcional)]",
        "flags": {"-p": "Fban com prova"},
    },
    allow_bots=False,
    allow_channels=False,
)
async def fban_(message: Message):
    """Bane um usuario das feds conectadas."""
    user, reason = message.extract_user_and_text
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBanned {}</b>"]
    await message.edit(fban_arg[0])
    error_msg = "Forneça uma ID de usuário ou responda a um usuário"
    if user is None:
        return await message.err(error_msg, del_in=7)
    try:
        user_ = await message.client.get_users(user)
    except (PeerIdInvalid, IndexError):
        return await message.err(error_msg, del_in=7)
    user = user_.id
    if (
        user in Config.SUDO_USERS
        or user in Config.OWNER_ID
        or user == (await message.client.get_me()).id
    ):
        return await message.err(
            "Não é possível F-Ban usuário que existe no Sudo ou Proprietário", del_in=7
        )
    failed = []
    total = 0
    reason = reason or "Não especificado."
    reply = message.reply_to_message
    with_proof = bool("-p" in message.flags and reply)
    await message.edit(fban_arg[1])
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["chat_id"])
        if with_proof:
            try:
                await reply.forward(chat_id)
            except Forbidden:
                # Can't send media
                pass
        try:
            async with kannax.conversation(chat_id, timeout=8) as conv:
                await conv.send_message(f"/fban {user} {reason}")
                response = await conv.get_response(
                    mark_read=True,
                    filters=(filters.user([609517172]) & ~filters.service),
                )
                resp = response.text.lower()
                if not (
                    ("novo fedban" in resp)
                    or ("iniciando um fedban" in resp)
                    or ("iniciar um fedban" in resp)
                    or ("razão de fedban atualizada" in resp)
                ):
                    failed.append(f"{data['fed_name']}  \n__ID__: `{data['chat_id']}`")
        except FloodWait as f:
            await asyncio.sleep(f.x + 3)
        except Exception:
            failed.append(data["fed_name"])
    if total == 0:
        return await message.err(
            "Você não tem feds conectadas! \nveja .help addf, para obter mais informações."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Falha fban em {len(failed)}/{total} feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Sucesso! Fbanned em `{total}` feds."
    msg_ = (
        fban_arg[3].format(user_.mention)
        + f"\n**Razão:** {reason}\n**Status:** {status}"
    )
    if with_proof:
        proof_link = (await reply.forward(Config.LOG_CHANNEL_ID)).link
        msg_ += f"\n\n<b>[ [PROOF]({proof_link}) ]</b>"
    await message.edit(msg_, log=__name__)


@kannax.on_cmd(
    "unfban",
    about={
        "header": "Unfban user",
        "description": "Retire o banimento do usuário da lista de feds",
        "usage": "{tr}unfban [username|responder o usuario|user_id]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def unfban_(message: Message):
    """Cancela o ban de um usuário das feds conectadas."""
    user = (message.extract_user_and_text)[0]
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>Un-FBanned {}</b>"]
    await message.edit(fban_arg[0])
    error_msg = "Forneça uma ID de usuário ou responda a um usuário"
    if user is None:
        return await message.err(error_msg, del_in=7)
    try:
        user_ = await message.client.get_users(user)
    except (PeerIdInvalid, IndexError):
        return await message.err(error_msg, del_in=7)
    user = user_.id
    failed = []
    total = 0
    await message.edit(fban_arg[1])
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["chat_id"])
        try:
            async with kannax.conversation(chat_id, timeout=8) as conv:
                await conv.send_message(f"/unfban {user}")
                response = await conv.get_response(
                    mark_read=True,
                    filters=(filters.user([609517172]) & ~filters.service),
                )
                resp = response.text.lower()
                if not (
                    ("new un-fedban" in resp)
                    or ("i'll give" in resp)
                    or ("un-fedban" in resp)
                ):
                    failed.append(f"{data['fed_name']}  \n__ID__: `{data['chat_id']}`")

        except BaseException:
            failed.append(data["fed_name"])
    if total == 0:
        return await message.err(
            "Você não tem feds conectados! \nveja .help addf, para obter mais informações."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Falha ao anular o fban em `{len(failed)}/{total}` feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Successo! Un-Fbanned em `{total}` feds."
    msg_ = fban_arg[3].format(user_.mention) + f"\n**Status:** {status}"
    await message.edit(msg_, log=__name__)


@kannax.on_cmd(
    "listf",
    about={
        "header": "Fed Chat List",
        "description": "Obtenha uma lista de chats adicionados na fed",
        "usage": "{tr}listf",
    },
)
async def fban_lst_(message: Message):
    """Liste todos as feds conectados."""
    out = ""
    async for data in FED_LIST.find():
        out += f"• <i>ID<b/i>: `{data['chat_id']}`\n  Fed: <b>{data['fed_name']}</b>\n"
    await message.edit_or_send_as_file(
        "**Federações conectadas:**\n\n" + out
        if out
        else "**Você ainda não se conectou a nenhuma federação!**",
        caption="Lista Feds Conectadas",
    )
