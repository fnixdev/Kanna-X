"""Fun plugin"""

import asyncio

from pyrogram import __version__ as __pyro_version__
from pyrogram import filters
from pyrogram.errors import BadRequest, Forbidden
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from kannax import Config, Message, get_version, kannax, get_collection
from kannax.core.ext import RawClient
from kannax.versions import __python_version__
from kannax.plugins.utils.telegraph import upload_media_
from kannax.utils import rand_array


SAVED_SETTINGS = get_collection("CONFIGS")
SAVED = get_collection("ALIVE_DB")

LOGGER = kannax.getLogger(__name__)

media_ = None


async def _init() -> None:
    _AliveMsg = await SAVED.find_one({"_id": "CUSTOM_MSG"})
    if _AliveMsg:
        ALIVE_MSG = _AliveMsg["data"]
    media_ = await SAVED_SETTINGS.find_one({"_id": "ALIVE_MEDIA"})
    if media_:
        Config.NEW_ALIVE_MEDIA = media_["url"]
        Config.ALIVE_MEDIA_TYPE = media_["type"]
    else:
        Config.NEW_ALIVE_MEDIA = "https://telegra.ph/file/4e956ef52c931570fb110.png"
        Config.ALIVE_MEDIA_TYPE = "photo"


@kannax.on_cmd(
    "setimedia",
    about={
        "header": "set alive media",
        "flags": {
            "-c": "check alive media.",
            "-r": "reset alive media.",
        },
        "usage": "{tr}setimedia [reply media]",
    },
)
async def set_alive_media(message: Message):
    """set alive media"""
    found = await SAVED_SETTINGS.find_one({"_id": "ALIVE_MEDIA"})
    if "-c" in message.flags:
        if found:
            media_ = found["url"]
        else:
            media_ = "https://telegra.ph/file/4e956ef52c931570fb110.png"
        return await message.edit(f"[<b>Esta</b>]({media_}) é sua Alive Media atual")
    elif "-r" in message.flags:
        if not found:
            return await message.edit("`Você ainda não definiu nenhuma media para ialive.`", del_in=5)
        await SAVED_SETTINGS.delete_one({"_id": "ALIVE_MEDIA"})
        await message.edit("`Alive Media foi resetada para o padrão. Reiniciando...`", del_in=5)
        asyncio.get_event_loop().create_task(kannax.restart())
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit(
            "`Responda a alguma Media para defini-la como seu Alive.`", del_in=5
        )
    type_ = msg_type_alive(reply_)
    if type_ not in ["gif", "photo", "video"]:
        return await message.edit("`Formato não suportado.`", del_in=5)
    link_ = await upload_media_(message)
    whole_link = f"https://telegra.ph{link_}"
    await SAVED_SETTINGS.update_one(
        {"_id": "ALIVE_MEDIA"}, {"$set": {"url": whole_link}}, upsert=True
    )
    await SAVED_SETTINGS.update_one(
        {"_id": "ALIVE_MEDIA"}, {"$set": {"type": type_}}, upsert=True
    )
    await message.edit(
        f"`Alive media definida. O bot esta reiniciando aguarde 5 segundos...`"
    )
    asyncio.get_event_loop().create_task(kannax.restart())


@kannax.on_cmd("ialive", about={"header": "Just For Fun"}, allow_channels=False)
async def alive_inline(message: Message):
    try:
        if message.client.is_bot:
            await send_alive_message(message)
        elif kannax.has_bot:
            try:
                await send_inline_alive(message)
            except BadRequest:
                await send_alive_message(message)
        else:
            await send_alive_message(message)
    except Exception as e_all:
        await message.err(str(e_all), del_in=10, log=__name__)


async def send_alive_message(message: Message) -> None:
    global _USER_CACHED_MEDIA, _BOT_CACHED_MEDIA
    chat_id = message.chat.id
    client = message.client
    caption = await Bot_Alive.alive_info()
    if client.is_bot:
        reply_markup = Bot_Alive.alive_buttons()
    else:
        reply_markup = None
    if Config.ALIVE_MEDIA_TYPE == "photo":
        await client.send_photo(
            chat_id,
            photo=Config.NEW_ALIVE_MEDIA,
            caption=caption,
            reply_markup=reply_markup,
        )
    elif Config.ALIVE_MEDIA_TYPE == "gif" or "video":
        await client.send_animation(
            chat_id,
            animation=Config.NEW_ALIVE_MEDIA,
            caption=caption,
            reply_markup=reply_markup,
        )


async def send_inline_alive(message: Message) -> None:
    _bot = await kannax.bot.get_me()
    try:
        i_res = await kannax.get_inline_bot_results(_bot.username, "alive")
        i_res_id = (
            (
                await kannax.send_inline_bot_result(
                    chat_id=message.chat.id,
                    query_id=i_res.query_id,
                    result_id=i_res.results[0].id,
                )
            )
            .updates[0]
            .id
        )
    except (Forbidden, BadRequest) as ex:
        await message.err(str(ex), del_in=5)
        return
    await message.delete()
    await asyncio.sleep(200)
    await kannax.delete_messages(message.chat.id, i_res_id)


def msg_type_alive(message):
    type_ = "text"
    if message.audio:
        type_ = "audio"
    elif message.animation:
        type_ = "gif"
    elif message.photo:
        type_ = "photo"
    elif message.sticker:
        type_ = "sticker"
    elif message.video:
        type_ = "video"
    elif message.document.file_name.endswith((".gif", ".mp4", "webm")):
        type_ = "gif"
    elif message.document.file_name.endswith((".jpeg", ".png", ".jpg", "webp")):
        type_ = "photo"
    return type_


if kannax.has_bot:

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^status_alive$"))
    async def status_alive_(_, c_q: CallbackQuery):
        c_q.from_user.id
        await c_q.answer(
            f"""
▫️ Modo :  {Bot_Alive._get_mode()}
▫️ Uptime  :  {kannax.uptime}
▫️ Python  :  v{__python_version__}
▫️ Version  :  v{get_version()}
▫️ Pyrogram  :  v{__pyro_version__}
""", show_alert=True,
        )
        return status_alive_

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^settings_btn$"))
    async def alive_cb(_, c_q: CallbackQuery):
        alive_s = "➕ ᴘʟᴜɢɪɴs + : {}\n".format(
            _parse_arg(Config.LOAD_UNOFFICIAL_PLUGINS)
        )
        alive_s += f"👥 ᴀɴᴛɪsᴘᴀᴍ : {_parse_arg(Config.SUDO_ENABLED)}\n"
        alive_s += f"🚨 ᴀɴᴛɪsᴘᴀᴍ : {_parse_arg(Config.ANTISPAM_SENTRY)}\n"
        if Config.HEROKU_APP and Config.RUN_DYNO_SAVER:
            alive_s += "⛽️ ᴅʏɴᴏ :  ✅ ᴀᴛɪᴠᴀᴅᴏ\n"
        alive_s += f"💬 ʙᴏᴛ ꜰᴡᴅ : {_parse_arg(Config.BOT_FORWARDS)}\n"
        alive_s += f"🛡 ᴘᴍ ʙʟᴏᴄᴋ : {_parse_arg(not Config.ALLOW_ALL_PMS)}\n"
        alive_s += f"📝 ʟᴏɢ ᴘᴍ : {_parse_arg(Config.PM_LOGGING)}"
        await c_q.answer(alive_s, show_alert=True)
        await asyncio.sleep(0.5)


def _parse_arg(arg: bool) -> str:
    return " ✅ ᴀᴛɪᴠᴀᴅᴏ" if arg else " ❎ ᴅᴇsᴀᴛɪᴠᴀᴅᴏ"


class Bot_Alive:
    @staticmethod
    async def alive_info() -> str:
        _findamsg = await SAVED.find_one({"_id": "ALIVE_MSG"})
        if _findamsg is None:
            mmsg = rand_array(FRASES)
        else:
            mmsg = _findamsg.get("data")
        alive_info_ = f"""
ᴏɪ ᴍᴇsᴛʀᴇ, ᴋᴀɴɴᴀx ɪ'ᴛs ᴀʟɪᴠᴇ

{mmsg}
"""
        return alive_info_

    @staticmethod
    def _get_mode() -> str:
        if RawClient.DUAL_MODE:
            return "DUAL"
        if Config.BOT_TOKEN:
            return "BOT"
        return "USER"

    @staticmethod
    def alive_buttons() -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton(
                    text="⚙️  ᴄᴏɴꜰɪɢ", callback_data="settings_btn"),
                InlineKeyboardButton(
                    text="💭  sᴛᴀᴛᴜs", callback_data="status_alive"),
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def alive_default_imgs() -> str:
        alive_imgs = [
            "https://telegra.ph/file/4ae6e1ce6a10ba89940fd.gif",
            "https://telegra.ph/file/505c324dd185c6e5ddc69.gif",
            "https://telegra.ph/file/8e99348c3ecdbd23c7a40.gif",
            "https://telegra.ph/file/c64de99e926b05c80eaa6.gif",
            "https://telegra.ph/file/1b0209fcfe45afe2f5f44.gif",
            "https://telegra.ph/file/5e2ae141d3f7d1e303ddf.gif",
            "https://telegra.ph/file/a5f304555673c0b9911a5.gif",
        ]
        return rand_array(alive_imgs)


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
