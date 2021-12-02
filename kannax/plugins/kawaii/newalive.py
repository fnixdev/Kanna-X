# new alive plugin for KannaX by @fnixdev

"""novo alive para kannax"""

from kannax import Message, get_collection, kannax, get_version
from kannax.utils import rand_array
from kannax.plugins.bot.ialive import Bot_Alive 
from kannax.versions import __python_version__
from telegraph import upload_file

SAVED = get_collection("ALIVE_DB")

ALIVE_MSG = {}

async def _init():
    global ALIVE_MEDIA, ALIVE_MSG  # pylint: disable=global-statement
    link = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    if link:
        ALIVE_MEDIA = link["link"]
    _AliveMsg = await SAVED.find_one({"_id": "CUSTOM_MSG"})
    if _AliveMsg:
        ALIVE_MSG = _AliveMsg["data"]


@kannax.on_cmd(
    "setamedia",
    about={
        "header": "Set alive media",
        "description": "Voçê pode definir uma mídia para aparecer em seu Alive",
    },
)
async def ani_save_media_alive(message: Message):
    """set media alive"""
    query = message.input_str
    replied = message.reply_to_message
    if replied:
        file = await kannax.download_media(replied)
        iurl = upload_file(file)
        media = f"https://telegra.ph{iurl[0]}"
        await SAVED.update_one(
            {"_id": "ALIVE_MEDIA"}, {"$set": {"link": media}}, upsert=True
        )
        await message.edit("`Alive Media definida com sucesso!`", del_in=5, log=True)
    elif query:
        await SAVED.update_one(
                        {"_id": "ALIVE_MEDIA"}, {"$set": {"link": query}}, upsert=True
        )
        await message.edit("`Alive Media definida com sucesso!`", del_in=5, log=True)
    else:
        await message.err("Invalid Syntax")


@kannax.on_cmd(
    "setamsg",
    about={
        "header": "Define uma mensagem para alive",
        "description": "Voçê pode definir uma mensagem para aparecer em seu Alive",
    },
)
async def save_msg_alive(message: Message):
    """set alive msg"""
    rep = message.input_or_reply_str
    if not rep:
        return await message.edit("`Você precisa digitar ou responder a uma mensagem pra salva-la`", del_in=6)
    if rep:
        await SAVED.update_one(
            {"_id": "ALIVE_MSG"}, {"$set": {"data": rep}}, upsert=True
        )
        await message.edit("`Mensagem para alive definida com sucesso!`", del_in=5, log=True)
    else:
        await message.err("Invalid Syntax")


@kannax.on_cmd(
    "alive",
    about={
        "header": "Alive apenas",
    },
)
async def view_del_ani(message: Message):
    """new alive"""
    _findpma = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    _findamsg = await SAVED.find_one({"_id": "ALIVE_MSG"})
    if _findpma is None:
        return await message.err("`Alive Media não está definida.`", del_in=5)
    if _findamsg is None:
        mmsg = rand_array(FRASES)
    else:
        mmsg = _findamsg.get("data")
    media = _findpma.get("link")
    msg = "ᴏɪ ᴍᴇsᴛʀᴇ, ᴋᴀɴɴᴀx ɪ'ᴛs ᴀʟɪᴠᴇ"
    alive_msg = f"""
{msg}

{mmsg}

• **Modo** :  `{Bot_Alive._get_mode()}`
• **Uptime**  :  `{kannax.uptime}`
• **Bot Version**  :  `v{get_version()}`
• **Python Version**  :  `v{__python_version__}`

    ✨ [sᴜᴘᴏʀᴛᴇ ](https://t.me/fnixsup) | 👾 [ʀᴇᴘᴏ](https://github.com/fnixdev/Kanna-X)
"""
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
    await message.delete()


@kannax.on_cmd(
    "delamsg",
    about={
        "header": "Delete alive message",
        "description": "Retorna a mensagem de Alive「 para o padrão",
      },
)
async def del_a_msg(message: Message):
    """del msg alive"""
    _findamsg = await SAVED.find_one({"_id": "ALIVE_MSG"})
    if _findamsg is None:
        await message.edit("`Você ainda não definiu uma mensagem para Alive`", del_in=5)
    else:
        await SAVED.find_one_and_delete({"_id": "ALIVE_MSG"})
        await message.edit("`Alive msg excluida`", del_in=5, log=True)
 

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