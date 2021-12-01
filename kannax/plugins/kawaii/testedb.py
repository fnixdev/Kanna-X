from kannax import Message, get_collection, kannax, get_version
from kannax.utils import rand_array
from kannax.plugins.bot.alive import Bot_Alive 
from kannax.versions import __python_version__
from telegraph import upload_file
from pyrogram.errors import MediaEmpty, WebpageCurlFailed

SAVED = get_collection("TESTE_DB")


async def _init():
    global ALIVE_MEDIA, ALIVE_MSG  # pylint: disable=global-statement
    link = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    if link:
        ALIVE_MEDIA = link["link"]
    _AliveMsg = await SAVED.find_one({"_id": "CUSTOM_MSG"})
    if _AliveMsg:
        ALIVE_MSG = _AliveMsg.get("data")


@kannax.on_cmd(
    "setamedia",
    about={
        "header": "Define uma mídia para alive",
    },
)
async def ani_save_media_alive(message: Message):
    """Set Media DB"""
    query = message.input_str
    replied = message.reply_to_message
    if replied:
        file = await kannax.download_media(replied)
        iurl = upload_file(file)
        media = f"https://telegra.ph{iurl[0]}"
        await SAVED.update_one(
            {"_id": "ALIVE_MEDIA"}, {"$set": {"link": media}}, upsert=True
        )
        await message.edit("`Alive Media definida com sucesso!`")
    elif query:
        await SAVED.update_one(
                        {"_id": "ALIVE_MEDIA"}, {"$set": {"link": query}}, upsert=True
        )
        await message.edit("`Alive Media definida com sucesso!`")
    else:
        await message.err("Invalid Syntax")


@kannax.on_cmd(
    "setamsg",
    about={
        "header": "Define uma mensagem para alive",
    },
)
async def ani_save_media_alive(message: Message):
    """Set alive msg"""
    query = message.input_str
    replied = message.reply_to_message
    if replied.text:
        await SAVED.update_one(
            {"_id": "ALIVE_MSG"}, {"$set": {"data": replied}}, upsert=True
        )
        await message.edit("`Mensagem para alive definida com sucesso!`")
    elif query:
        await SAVED.update_one(
                        {"_id": "ALIVE_MSG"}, {"$set": {"data": query}}, upsert=True
        )
        await message.edit("`Mensagem para alive definida com sucesso!`")
    else:
        await message.err("Invalid Syntax")


@kannax.on_cmd(
    "aliv",
    about={
        "header": "Alive Media Settings",
    },
)
async def view_del_ani(message: Message):
    _findpma = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    _findamsg = await SAVED.find_one({"_id": "ALIVE_MSG"})
    if _findpma is None:
        return await message.err("`Alive Media não está definida.`")
    if _findamsg is None:
        mmsg = rand_array(FRASES)
    else:
        mmsg = _findamsg.get("data")
    media = ""
    msg = "ᴏɪ ᴍᴇsᴛʀᴇ, ᴋᴀɴɴᴀx ɪ'ᴛs ᴀʟɪᴠᴇ"
    alive_msg = f"""
{msg}

   {mmsg}

▫️ Modo :  `{Bot_Alive._get_mode()}`
▫️ Uptime  :  `{kannax.uptime}`
▫️ Bot Version  :  `v{get_version()}`
▫️ Python Version  :  `v{__python_version__}`
"""
    async for link in SAVED.find():
        media += f"{link['link']}"
    if media.endswith((".gif", ".mp4")):
        await message.client.send_animation(
            chat_id=message.chat.id,
            animation=media,
            caption=alive_msg
        )
    else:
        await message.client.send_photo(
            chat_id=message.chat.id, photo=media, caption=alive_msg
        )


@kannax.on_cmd(
    "delamsg",
    about={
        "header": "Delete mídia",
        "description": "Voçê pode voltar para a animação padrão com esse comando",
      },
    allow_channels=False,
)
async def ani_del_a_msg(message: Message):
    _findamsg = await SAVED.find_one({"_id": "ALIVE_MSG"})
    if _findamsg is None:
        await message.edit("`Você ainda não definiu uma mensagem para Alive`")
    else:
        await SAVED.find_one_and_delete({"_id": "ALIVE_MSG"})
        await message.edit("`Alive msg excluida`", del_in=3, log=True)
 

FRASES = (
    "ʟᴇᴍʙʀᴇ-sᴇ ᴅᴀ ʟɪᴄ̧ᴀ̃ᴏ ᴇ ɴᴀ̃ᴏ ᴅᴀ ᴅᴇᴄᴇᴘᴄ̧ᴀ̃ᴏ.",
    "ᴠᴏᴄᴇ̂ ɴᴀ̃ᴏ ᴄᴏɴʜᴇᴄᴇ ᴀs ᴘᴇssᴏᴀs, ᴠᴏᴄᴇ̂ ᴄᴏɴʜᴇᴄᴇ ᴀᴘᴇɴᴀs ᴏ ǫᴜᴇ ᴇʟᴀs ᴘᴇʀᴍɪᴛᴇᴍ ǫᴜᴇ ᴠᴏᴄᴇ̂ ᴠᴇᴊᴀ.",
    "ᴀs ᴠᴇᴢᴇs ᴀs ǫᴜᴇsᴛᴏ̃ᴇs sᴀ̃ᴏ ᴄᴏᴍᴘʟɪᴄᴀᴅᴀs ᴇ ᴀs ʀᴇsᴘᴏsᴛᴀs sᴀ̃ᴏ sɪᴍᴘʟᴇs.",
    "ᴀᴍᴀʀ ᴀʟɢᴜᴇ́ᴍ ᴘʀᴏꜰᴜɴᴅᴀᴍᴇɴᴛᴇ ʟʜᴇ ᴅᴀ́ ꜰᴏʀᴄ̧ᴀ; sᴇʀ ᴀᴍᴀᴅᴏ ᴘʀᴏꜰᴜɴᴅᴀᴍᴇɴᴛᴇ ʟʜᴇ ᴅᴀ́ ᴄᴏʀᴀɢᴇᴍ.",
    "ᴠᴏᴄᴇ̂ ɴᴀ̃ᴏ ᴇ́ ᴅᴇʀʀᴏᴛᴀᴅᴏ ǫᴜᴀɴᴅᴏ ᴘᴇʀᴅᴇ, ᴍᴀs sɪᴍ ǫᴜᴀɴᴅᴏ ᴠᴏᴄᴇ̂ ᴅᴇsɪsᴛᴇ.",
    "ʜᴀ ᴍᴏᴍᴇɴᴛᴏs ǫᴜᴇ ᴠᴏᴄᴇ̂ ᴘʀᴇᴄɪsᴀ ᴅᴇsɪsᴛɪʀ ᴅᴇ ᴀʟɢᴜᴍᴀ ᴄᴏɪsᴀ ᴘᴀʀᴀ ᴘʀᴇsᴇʀᴠᴀʀ ᴀ ᴏᴜᴛʀᴀ.",
    "ᴀ ᴠɪᴅᴀ ᴅᴀs ᴘᴇssᴏᴀs ɴᴀ̃ᴏ ᴀᴄᴀʙᴀ ǫᴜᴀɴᴅᴏ ᴇʟᴀs ᴍᴏʀʀᴇᴍ, ᴍᴀs sɪᴍ ǫᴜᴀɴᴅᴏ ᴘᴇʀᴅᴇᴍ ᴀ ꜰᴇ́.",
    "sᴇ ᴠᴏᴄᴇ̂ ᴇsᴛᴀ́ ᴠɪᴠᴏ ᴘᴏᴅᴇ ʀᴇᴄᴏᴍᴇᴄ̧ᴀʀ. ɴɪɴɢᴜᴇ́ᴍ ᴛᴇᴍ ᴏ ᴅɪʀᴇɪᴛᴏ ᴅᴇ ᴛᴇ ᴛɪʀᴀʀ ɪssᴏ.",
    "ᴏ ᴘᴇssɪᴍɪsᴍᴏ, ᴅᴇᴘᴏɪs ᴅᴇ ᴠᴏᴄᴇ̂ sᴇ ᴀᴄᴏsᴛᴜᴍᴀʀ ᴀ ᴇʟᴇ, ᴇ́ ᴛᴀ̃ᴏ ᴀɢʀᴀᴅᴀ́ᴠᴇʟ ǫᴜᴀɴᴛᴏ ᴏ ᴏᴛɪᴍɪsᴍᴏ.",
    "ᴘᴇʀᴅᴏᴀʀ ᴇ́ ʟɪʙᴇʀᴛᴀʀ ᴏ ᴘʀɪsɪᴏɴᴇɪʀᴏ... ᴇ ᴅᴇsᴄᴏʙʀɪʀ ǫᴜᴇ ᴏ ᴘʀɪsɪᴏɴᴇɪʀᴏ ᴇʀᴀ ᴠᴏᴄᴇ̂.",
    "ᴛᴜᴅᴏ ᴏ ǫᴜᴇ ᴜᴍ sᴏɴʜᴏ ᴘʀᴇᴄɪsᴀ ᴇ́ ᴀʟɢᴜᴇ́ᴍ ǫᴜᴇ ᴀᴄʀᴇᴅɪᴛᴇ ǫᴜᴇ ᴇʟᴇ ᴘᴏssᴀ sᴇʀ ʀᴇᴀʟɪᴢᴀᴅᴏ.",
    "ɴᴀ̃ᴏ ᴇsᴘᴇʀᴇ ᴘᴏʀ ᴜᴍᴀ ᴄʀɪsᴇ ᴘᴀʀᴀ ᴅᴇsᴄᴏʙʀɪʀ ᴏ ǫᴜᴇ ᴇ́ ɪᴍᴘᴏʀᴛᴀɴᴛᴇ ᴇᴍ sᴜᴀ ᴠɪᴅᴀ.",
    "ᴏ ᴘᴇssɪᴍɪsᴍᴏ, ᴅᴇᴘᴏɪs ᴅᴇ ᴠᴏᴄᴇ̂ sᴇ ᴀᴄᴏsᴛᴜᴍᴀʀ ᴀ ᴇʟᴇ, ᴇ́ ᴛᴀ̃ᴏ ᴀɢʀᴀᴅᴀ́ᴠᴇʟ ǫᴜᴀɴᴛᴏ ᴏ ᴏᴛɪᴍɪsᴍᴏ.",
    "ᴅᴇsᴄᴏʙʀɪʀ ᴄᴏɴsɪsᴛᴇ ᴇᴍ ᴏʟʜᴀʀ ᴘᴀʀᴀ ᴏ ǫᴜᴇ ᴛᴏᴅᴏ ᴍᴜɴᴅᴏ ᴇsᴛᴀ́ ᴠᴇɴᴅᴏ ᴇ ᴘᴇɴsᴀʀ ᴜᴍᴀ ᴄᴏɪsᴀ ᴅɪꜰᴇʀᴇɴᴛᴇ.",
    "ɴᴏ ꜰᴜɴᴅᴏ ᴅᴇ ᴜᴍ ʙᴜʀᴀᴄᴏ ᴏᴜ ᴅᴇ ᴜᴍ ᴘᴏᴄ̧ᴏ, ᴀᴄᴏɴᴛᴇᴄᴇ ᴅᴇsᴄᴏʙʀɪʀ-sᴇ ᴀs ᴇsᴛʀᴇʟᴀs.",
)