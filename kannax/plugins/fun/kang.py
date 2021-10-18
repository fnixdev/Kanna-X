""" kang stickers """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

import io
import os
import random

from bs4 import BeautifulSoup as bs
from PIL import Image
from pyrogram import emoji
from pyrogram.errors import StickersetInvalid, YouBlockedUser
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName

from kannax import Config, Message, kannax
from kannax.utils import get_response


@kannax.on_cmd(
    "kang",
    about={
        "header": "rouba stickers ou cria novos",
        "flags": {"-s": "sem link", "-d": "sem deixar vestígios"},
        "usage": "responda {tr}kang [emoji('s)] [numero do pack] a um sticker ou "
        "uma imagem para colocá-la em seu pacote de userbot.",
        "examples": [
            "{tr}kang",
            "{tr}kang -s",
            "{tr}kang -d",
            "{tr}kang 🤔",
            "{tr}kang 2",
            "{tr}kang 🤔 2",
        ],
    },
    allow_channels=False,
    allow_via_bot=False,
)
async def kang_(message: Message):
    """kang um sticker"""
    user = await kannax.get_me()
    replied = message.reply_to_message
    photo = None
    emoji_ = None
    is_anim = False
    resize = False
    if replied and replied.media:
        if replied.photo:
            resize = True
        elif replied.document and "image" in replied.document.mime_type:
            resize = True
        elif replied.document and "tgsticker" in replied.document.mime_type:
            is_anim = True
        elif replied.sticker:
            if not replied.sticker.file_name:
                await message.edit("`O sticker não tem nome!`")
                return
            emoji_ = replied.sticker.emoji
            is_anim = replied.sticker.is_animated
            if not replied.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            await message.edit("`Arquivo não suportado!`")
            return
        await message.edit(f"`{random.choice(KANGING_STR)}`")
        photo = await kannax.download_media(message=replied, file_name=Config.DOWN_PATH)
    else:
        await message.edit("`Eu não posso roubar isso...`")
        return
    if photo:
        args = message.filtered_input_str.split()
        pack = 1
        if len(args) == 2:
            emoji_, pack = args
        elif len(args) == 1:
            if args[0].isnumeric():
                pack = int(args[0])
            else:
                emoji_ = args[0]

        if emoji_ and emoji_ not in (
            getattr(emoji, _) for _ in dir(emoji) if not _.startswith("_")
        ):
            emoji_ = None
        if not emoji_:
            emoji_ = "🤔"

        u_name = user.username
        u_name = "@" + u_name if u_name else user.first_name or user.id
        packname = f"a{user.id}_by_x_{pack}"
        custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}'s kang pack"
        packnick = f"{custom_packnick} Vol.{pack}"
        cmd = "/newpack"
        if resize:
            photo = resize_photo(photo)
        if is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"
        exist = False
        try:
            exist = await message.client.send(
                GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname))
            )
        except StickersetInvalid:
            pass
        if exist is not False:
            async with kannax.conversation("Stickers", limit=30) as conv:
                try:
                    await conv.send_message("/addsticker")
                except YouBlockedUser:
                    await message.edit("first **unblock** @Stickers")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                msg = await conv.get_response(mark_read=True)
                limit = "50" if is_anim else "120"
                while limit in msg.text:
                    pack += 1
                    packname = f"a{user.id}_by_kannax_{pack}"
                    packnick = f"{custom_packnick} Vol.{pack}"
                    if is_anim:
                        packname += "_anim"
                        packnick += " (Animated)"
                    await message.edit(
                        "`Mudando para Pack "
                        + str(pack)
                        + " devido ao espaço insuficiente`"
                    )
                    await conv.send_message(packname)
                    msg = await conv.get_response(mark_read=True)
                    if msg.text == "Pacote inválido selecionado.":
                        await conv.send_message(cmd)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packnick)
                        await conv.get_response(mark_read=True)
                        await conv.send_document(photo)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(emoji_)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response(mark_read=True)
                            await conv.send_message(f"<{packnick}>", parse_mode=None)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/skip")
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packname)
                        await conv.get_response(mark_read=True)
                        if "-d" in message.flags:
                            await message.delete()
                        else:
                            out = (
                                "__kanged__"
                                if "-s" in message.flags
                                else f"[roubado](t.me/addstickers/{packname})"
                            )
                            await message.edit(
                                f"**Sticker** {out} __em um pacote diferente__**!**"
                            )
                        return
                await conv.send_document(photo)
                rsp = await conv.get_response(mark_read=True)
                if "Desculpe, o tipo de arquivo é inválido." in rsp.text:
                    await message.edit(
                        "`Falha ao adicionar sticker, use` @Stickers "
                        "`bot para adicionar o sticker manualmente.`"
                    )
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message("/done")
                await conv.get_response(mark_read=True)
        else:
            await message.edit("`Preparando um novo pacote...`")
            async with kannax.conversation("Stickers") as conv:
                try:
                    await conv.send_message(cmd)
                except YouBlockedUser:
                    await message.edit("primeiro **desbloqueie** @Stickers")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packnick)
                await conv.get_response(mark_read=True)
                await conv.send_document(photo)
                rsp = await conv.get_response(mark_read=True)
                if "Desculpe, o tipo de arquivo é inválido." in rsp.text:
                    await message.edit(
                        "`Falha ao adicionar sticker, use` @Stickers "
                        "`bot para adicionar o sticker manualmente.`"
                    )
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response(mark_read=True)
                    await conv.send_message(f"<{packnick}>", parse_mode=None)
                await conv.get_response(mark_read=True)
                await conv.send_message("/skip")
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                await conv.get_response(mark_read=True)
        if "-d" in message.flags:
            await message.delete()
        else:
            out = (
                "__kanged__"
                if "-s" in message.flags
                else f"[roubado](t.me/addstickers/{packname})"
            )
            await message.edit(f"**Sticker** {out}**!**")
        if os.path.exists(str(photo)):
            os.remove(photo)


@kannax.on_cmd(
    "stkrinfo",
    about={
        "header": "obter informações do pacote de sticker",
        "usage": "responda {tr}stkrinfo a qualquer sticker",
    },
)
async def sticker_pack_info_(message: Message):
    """obter informações do pacote de sticker"""
    replied = message.reply_to_message
    if not replied:
        await message.edit("`Não consigo obter informações do nada, posso ?!`")
        return
    if not replied.sticker:
        await message.edit("`Responda a um adesivo para obter os detalhes do pacote`")
        return
    await message.edit("`Buscando detalhes do pacote de adesivos, aguarde..`")
    get_stickerset = await message.client.send(
        GetStickerSet(
            stickerset=InputStickerSetShortName(short_name=replied.sticker.set_name)
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    out_str = (
        f"**Título do adesivo:** `{get_stickerset.set.title}\n`"
        f"**Sticker Nome curto:** `{get_stickerset.set.short_name}`\n"
        f"**Arquivado:** `{get_stickerset.set.archived}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Masks:** `{get_stickerset.set.masks}`\n"
        f"**Animado:** `{get_stickerset.set.animated}`\n"
        f"**Stickers no pacote:** `{get_stickerset.set.count}`\n"
        f"**Emojis no pacote:**\n{' '.join(pack_emojis)}"
    )
    await message.edit(out_str)


def resize_photo(photo: str) -> io.BytesIO:
    """Redimensione a foto fornecida para 512x512"""
    image = Image.open(photo)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))
    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "sticker.png"
    image.save(resized_photo, "PNG")
    os.remove(photo)
    return resized_photo


KANGING_STR = (
    "Plagiando hehe...",
    "Convidando este adesivo pro meu pack kkk...",
    "Roubando esse sticker...",
    "Ei, esse é um adesivo legal!\nImporta se eu roubar?!..",
    "hehe me stel ur stikér\nhehe.",
    "Olhe ali (☉｡☉)!→\nEnquanto eu roubo isso...",
    "Ai carinha que mora logo ali, me passa um sticker",
)


# Based on:
# https://github.com/AnimeKaizoku/SaitamaRobot/blob/10291ba0fc27f920e00f49bc61fcd52af0808e14/SaitamaRobot/modules/stickers.py#L42
@kannax.on_cmd(
    "sticker",
    about={
        "header": "Pesquisar pacotes de adesivos",
        "usage": "Responda {tr}sticker ou " "{tr}sticker [texto]",
    },
)
async def sticker_search(message: Message):
    # search sticker packs
    reply = message.reply_to_message
    query_ = None
    if message.input_str:
        query_ = message.input_str
    elif reply and reply.from_user:
        query_ = reply.from_user.username or reply.from_user.id

    if not query_:
        return message.err(
            "responder a um usuário ou fornecer texto para pesquisar pacotes de adesivos", del_in=3
        )

    await message.edit(f'🔎 Procurando pacotes de adesivos para "`{query_}`"...')
    titlex = f'<b>Pacotes de adesivos para:</b> "<u>{query_}</u>"\n'
    sticker_pack = ""
    try:
        text = await get_response.text(
            f"https://combot.org/telegram/stickers?q={query_}"
        )
    except ValueError:
        return await message.err(
            "A resposta não foi 200!, Api está tendo alguns problemas\nTente novamente mais tarde.",
            del_in=5,
        )
    soup = bs(text, "lxml")
    results = soup.find_all("div", {"class": "sticker-pack__header"})
    for pack in results:
        if pack.button:
            title_ = (pack.find("div", {"class": "sticker-pack__title"})).text
            link_ = (pack.a).get("href")
            sticker_pack += f"\n• [{title_}]({link_})"
    if not sticker_pack:
        sticker_pack = "`❌ Não encontrado!`"
    await message.edit((titlex + sticker_pack), disable_web_page_preview=True)
