# Copyright (C) 2021 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

"""Módulo que lida com Bot PM"""

import asyncio
from collections import defaultdict
from datetime import date, datetime, timedelta
from re import compile as comp_regex
from typing import Optional, Union

from pyrogram import StopPropagation, filters
from pyrogram.errors import BadRequest, FloodWait, UserIsBlocked
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    User,
)

from kannax import Config, Message, get_collection, pool, kannax
from kannax.utils import check_owner, get_file_id

from .bot_forwards import ban_from_bot_pm

# Load from DB
SAVED_SETTINGS = get_collection("CONFIGS")
# Loggers
CHANNEL = kannax.getCLogger(__name__)
LOGGER = kannax.getLogger(__name__)
# User Checks
BOT_BAN = get_collection("BOT_BAN")
BOT_START = get_collection("BOT_START")
# Caches
_BOT_PM_MEDIA = None
_CACHED_INFO = {}
# Regex
_TG_LINK_REGEX = comp_regex(r"http[s]?://[\w.]+/(?:[c|s]/)?(\w+)/([0-9]+)")
# Pyrogram Filter
BotAntiFloodFilter = filters.create(lambda _, __, ___: Config.BOT_ANTIFLOOD)


class FloodConfig:
    BANNED_USERS = filters.user()
    USERS = defaultdict(list)
    MESSAGES = 3
    SECONDS = 6
    OWNER = filters.user(list(Config.OWNER_ID))
    ALERT = defaultdict(dict)
    AUTOBAN = 10


if kannax.has_bot:

    async def _init() -> None:
        s_o = await SAVED_SETTINGS.find_one({"_id": "BOT_ANTIFLOOD"})
        if s_o:
            Config.BOT_ANTIFLOOD = s_o["data"]
        await get_bot_pm_media()
        await get_bot_info()

    def start_filter() -> filters:
        async def func(_, __, m: Message) -> bool:
            text = m.text or m.caption
            bot_ = (await get_bot_info()).get("bot")
            username = "@" + bot_.uname if bot_ else ""
            pattern = comp_regex(f"(?i)^/start({username})?([\s]+)?$")
            m.matches = (list(pattern.finditer(text)) if text else None) or None
            return bool(
                (m.chat and m.chat.type == "private") and m.matches and not m.edit_date
            )

        return filters.create(func, "StartFilter")

    async def get_bot_pm_media() -> None:
        global _BOT_PM_MEDIA
        if not Config.BOT_MEDIA:
            _BOT_PM_MEDIA = get_file_id(await kannax.bot.get_messages("kannagifs", 6))
            return
        if Config.BOT_MEDIA.strip().lower() != "false":
            match = _TG_LINK_REGEX.search(Config.BOT_MEDIA)
            if match:
                from_chat = str(match.group(1))
                if from_chat.isdigit():
                    from_chat = int("-100" + from_chat)
                msg_id = int(match.group(2))
                try:
                    bot_m_fid = get_file_id(
                        await kannax.bot.get_messages(from_chat, msg_id)
                    )
                except Exception as b_m_err:
                    LOGGER.error(b_m_err)
                else:
                    _BOT_PM_MEDIA = bot_m_fid

    async def get_bot_info():
        """Proprietário do cache e informações do bot"""
        global _CACHED_INFO
        t_now = datetime.now()
        if not (
            _CACHED_INFO
            and _CACHED_INFO.get("time")
            and (_CACHED_INFO.get("time") > datetime.timestamp(t_now))
        ):
            try:
                owner_info = await kannax.bot.get_user_dict(
                    Config.OWNER_ID[0], attr_dict=True
                )
            except (BadRequest, IndexError):
                _CACHED_INFO["owner"] = Config.OWNER_ID[0]
                LOGGER.debug(
                    "Não consigo obter informações sobre o usuário em OWNER_ID !\n"
                    "Tente /start no bot ou verifique OWNER_ID var"
                )
            else:
                _CACHED_INFO["owner"] = owner_info
            finally:
                _CACHED_INFO["bot"] = await kannax.bot.get_user_dict(
                    "me", attr_dict=True
                )
                _CACHED_INFO["time"] = int(
                    datetime.timestamp(t_now + timedelta(days=1))
                )
        return _CACHED_INFO

    async def send_bot_media(
        message: Message, text: str, markup: InlineKeyboardMarkup
    ) -> None:
        if Config.BOT_MEDIA and Config.BOT_MEDIA.strip().lower() == "false":
            await message.reply(
                text, disable_web_page_preview=True, reply_markup=markup
            )
        else:
            if not _BOT_PM_MEDIA:
                await get_bot_pm_media()
            await message.reply_cached_media(
                file_id=_BOT_PM_MEDIA, caption=text, reply_markup=markup
            )

    async def check_new_bot_user(user: Union[int, str, User]) -> bool:
        user_ = await kannax.bot.get_user_dict(user, attr_dict=True)
        if user_.id in Config.OWNER_ID:
            found = True
        else:
            found = await BOT_START.find_one({"user_id": user_.id})
            if not found:
                start_date = str(date.today().strftime("%B %d, %Y")).replace(",", "")
                bot_start_msg = (
                    f"<b>[Novo Usuario](tg://openmessage?user_id={user_.id})</b> Iniciou seu bot.\n\n"
                    f"ID: <code>{user_.id}</code>\n"
                    f"Nome: {user_.flname}\n"
                    f"👤: {user_.mention}\n"
                )
                await asyncio.gather(
                    BOT_START.insert_one(
                        {
                            "firstname": user_.flname,
                            "user_id": user_.id,
                            "date": start_date,
                        }
                    ),
                    CHANNEL.log(bot_start_msg),
                )
        return not bool(found)

    def default_owner_start(from_user):
        start_msg = f"ᴏɪ ᴍᴇsᴛʀᴇ 🥰!\nᴄᴏᴍᴏ ᴘᴏssᴏ ʟʜᴇ sᴇʀ ᴜᴛɪʟ ʜᴏᴊᴇ?"
        btns = [
            [InlineKeyboardButton("➕ ᴀᴅɪᴄɪᴏɴᴀʀ ᴀ ᴜᴍ ɢʀᴜᴘᴏ", callback_data="add_to_grp")],
        ]
        return start_msg, btns

    @kannax.bot.on_message(start_filter())
    async def start_bot(_, message: Message):
        c_info = await get_bot_info()
        bot_ = c_info.get("bot")
        owner_ = c_info.get("owner")
        from_user = await kannax.bot.get_user_dict(message.from_user, attr_dict=True)
        if from_user.id in Config.OWNER_ID:
            start_msg, btns = default_owner_start(from_user)
        else:
            start_msg = f"""
ᴏʟᴀ ᴇsᴛʀᴀɴʜᴏ, ᴇᴜ sᴏᴜ ᴋᴀɴɴᴀ\nʙᴏᴛ ᴘᴇssᴏᴀʟ ᴅᴇ: {owner_.flname}
"""
            if Config.BOT_FORWARDS:
                start_msg += "`ᴠᴏᴄᴇ ᴘᴏᴅᴇ ᴇɴᴛʀᴀʀ ᴇᴍ ᴄᴏɴᴛᴀᴛᴏ ᴄᴏᴍ ᴍᴇᴜ ᴍᴇsᴛʀᴇ ᴜsᴀɴᴅᴏ ᴇsᴛᴇ ʙᴏᴛ!!\nᴇɴᴠɪᴇ sᴜᴀ ᴍᴇɴsᴀɢᴇᴍ, ᴠᴏᴜ ᴇɴᴛʀᴇɢᴀ-ʟᴀ.`"
            contact_url = (
                f"https://t.me/{owner_.uname}"
                if owner_.uname
                else f"tg://user?id={owner_.id}"
            )
            btns = [
                [
                    InlineKeyboardButton("👤  Contato", url=contact_url),
                    InlineKeyboardButton("✨  Updates", url="t.me/kannaxup"),
                ]
            ]
        try:
            await send_bot_media(message, start_msg, InlineKeyboardMarkup(btns))
        except FloodWait as e:
            await asyncio.sleep(e.x + 10)
        except Exception as bpm_e:
            await CHANNEL.log(
                f"**ERROR**: {str(bpm_e)}\n\nOcorreu um erro fatal durante o envio de bot Pm Media"
            )
        await check_new_bot_user(message.from_user)

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^add_to_grp$"))
    @check_owner
    async def add_to_grp(c_q: CallbackQuery):
        await c_q.answer()
        msg = "ᴍᴇ ᴀᴅɪᴄɪᴏɴᴇ ᴀ ᴜᴍ ɢʀᴜᴘᴏ \n\nʟᴇᴍʙʀᴇ-sᴇ ᴇᴜ ᴘʀᴇᴄɪsᴏ ᴅᴇ ᴘʀɪᴠɪʟᴇɢɪᴏs ᴀᴅᴍɪɴ ᴘᴀʀᴀ ꜰᴀʟᴀʀ"
        add_bot = f"http://t.me/{(await get_bot_info())['bot'].uname}?startgroup=start"
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("➕ᴀᴅɪᴄɪᴏɴᴀʀ", url=add_bot)],
                [InlineKeyboardButton("◀️ ᴠᴏʟᴛᴀʀ", callback_data="back_bot_pm")],
            ]
        )
        await c_q.edit_message_text(msg, reply_markup=buttons)

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^back_bot_pm$"))
    @check_owner
    async def back_bot_pm_(c_q: CallbackQuery):
        await c_q.answer()
        start_msg, btns = default_owner_start(
            await kannax.bot.get_user_dict(c_q.from_user, attr_dict=True)
        )
        await c_q.edit_message_text(start_msg, reply_markup=InlineKeyboardMarkup(btns))

    # >>> ############# | X Bot Antiflood | ############# <<< #

    async def send_flood_alert(user_id: Union[int, User]) -> None:
        user_ = await kannax.bot.get_user_dict(user_id, attr_dict=True)
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🚫  BAN", callback_data=f"bot_pm_ban_{user_.id}"
                    ),
                    InlineKeyboardButton(
                        "➖ Bot Antiflood [OFF]",
                        callback_data="toggle_bot-antiflood_off",
                    ),
                ]
            ]
        )
        found = False
        if FloodConfig.ALERT and (user_.id in FloodConfig.ALERT.keys()):
            found = True
            FloodConfig.ALERT[user_.id]["count"] += 1
            flood_count = FloodConfig.ALERT[user_.id]["count"]
        else:
            flood_count = FloodConfig.ALERT[user_.id]["count"] = 1

        flood_msg = (
            r"⚠️ <b>\\#Flood_PmBot//</b>"
            "\n\n"
            f"  ID: <code>{user_.id}</code>\n"
            f"  Nome: {user_.flname}\n"
            f"  👤 Usuario: {user_.mention}"
            f"\n\n**Está enviando spam para o seu bot !** ->  [ Flood rate **({flood_count})** ]\n"
            "__Ação rápida__: Ignorado pelo bot por um tempo."
        )

        if found:
            if flood_count >= FloodConfig.AUTOBAN:
                if user_.id in Config.SUDO_USERS:
                    sudo_spam = (
                        f"**Sudo User** {user_.mention}:\n  ID: {user_.id}\n\n"
                        "Está flodando seu bot !, Verifique `.help delsudo` para remover o usuário do Sudo."
                    )
                    await kannax.bot.send_message(Config.LOG_CHANNEL_ID, sudo_spam)
                else:
                    await ban_from_bot_pm(
                        user_.id,
                        f"AutoBan para flood no bot [taxa de flood excedida de **({FloodConfig.AUTOBAN})**]",
                        log=__name__,
                    )
                    FloodConfig.USERS[user_.id].clear()
                    FloodConfig.ALERT[user_.id].clear()
                    FloodConfig.BANNED_USERS.remove(user_.id)
                return
            fa_id = FloodConfig.ALERT[user_.id].get("fa_id")
            if not fa_id:
                return
            try:
                msg_ = await kannax.bot.get_messages(Config.LOG_CHANNEL_ID, fa_id)
                if msg_.text != flood_msg:
                    await msg_.edit(flood_msg, reply_markup=buttons)
            except Exception as fa_id_err:
                LOGGER.debug(fa_id_err)
                return
        else:
            fa_msg = await kannax.bot.send_message(
                Config.LOG_CHANNEL_ID,
                flood_msg,
                reply_markup=buttons,
            )
            try:
                await kannax.bot.send_message(
                    Config.OWNER_ID[0],
                    f"⚠️  **[Bot Aviso Flood !]({fa_msg.link})**",
                )
            except UserIsBlocked:
                await CHANNEL.log("**Desbloqueie seu bot !**")
        if FloodConfig.ALERT[user_.id].get("fa_id") is None and fa_msg:
            FloodConfig.ALERT[user_.id]["fa_id"] = fa_msg.message_id

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^bot_pm_ban_([0-9]+)"))
    @check_owner
    async def bot_pm_ban_cb(c_q: CallbackQuery):
        user_id = int(c_q.matches[0].group(1))
        await asyncio.gather(
            c_q.answer(f"Banindo UserID -> {user_id} ...", show_alert=False),
            ban_from_bot_pm(user_id, "Spamming Bot", log=__name__),
            c_q.edit_message_text(f"✅ **Banido com sucesso**  User ID: {user_id}"),
        )

    def time_now() -> Union[float, int]:
        return datetime.timestamp(datetime.now())

    @pool.run_in_thread
    def is_flood(uid: int) -> Optional[bool]:
        """Verifica se um usuário está flodando"""
        FloodConfig.USERS[uid].append(time_now())
        if (
            len(
                list(
                    filter(
                        lambda x: time_now() - int(x) < FloodConfig.SECONDS,
                        FloodConfig.USERS[uid],
                    )
                )
            )
            > FloodConfig.MESSAGES
        ):
            FloodConfig.USERS[uid] = list(
                filter(
                    lambda x: time_now() - int(x) < FloodConfig.SECONDS,
                    FloodConfig.USERS[uid],
                )
            )
            return True

    @kannax.bot.on_message(
        filters.private & ~FloodConfig.OWNER & BotAntiFloodFilter, group=-100
    )
    async def antif_on_msg(_, msg: Message):
        user_id = msg.from_user.id
        if await BOT_BAN.find_one({"user_id": user_id}):
            # LOGGER.info(
            #     r"<b>\\#Bot_PM//</b>" f"\n\nBanned UserID: {user_id} ignorado do bot."
            # )
            await msg.stop_propagation()
        elif await is_flood(user_id):
            await send_flood_alert(msg.from_user)
            FloodConfig.BANNED_USERS.add(user_id)
            await msg.stop_propagation()
        elif user_id in FloodConfig.BANNED_USERS:
            FloodConfig.BANNED_USERS.remove(user_id)

    @kannax.bot.on_callback_query(~FloodConfig.OWNER & BotAntiFloodFilter, group=-100)
    async def antif_on_cb(_, c_q: CallbackQuery):
        user_id = c_q.from_user.id
        if await BOT_BAN.find_one({"user_id": user_id}):
            await c_q.answer("You are banned from this bot !")
            # LOGGER.info(
            #     r"<b>\\#Callback//</b>"
            #     f"\n\nBanned UserID: {user_id} ignorado do bot."
            # )
            raise StopPropagation
        if await is_flood(user_id):
            await c_q.answer("Wooh, Mate Chill ! vá devagar")
            await send_flood_alert(c_q.from_user)
            FloodConfig.BANNED_USERS.add(user_id)
            raise StopPropagation
        elif user_id in FloodConfig.BANNED_USERS:
            FloodConfig.BANNED_USERS.remove(user_id)

        ########################################################

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^toggle_bot-antiflood_off$"))
    @check_owner
    async def settings_toggle(c_q: CallbackQuery):
        Config.BOT_ANTIFLOOD = False
        await asyncio.gather(
            c_q.answer(),
            SAVED_SETTINGS.update_one(
                {"_id": "BOT_ANTIFLOOD"},
                {"$set": {"data": Config.BOT_ANTIFLOOD}},
                upsert=True,
            ),
            c_q.edit_message_text("BOT_ANTIFLOOD agora está desabilitado !"),
        )


@kannax.on_cmd(
    "bot_users",
    about={
        "header": "Obtenha uma lista de usuários ativos que iniciaram seu bot",
        "examples": "{tr}bot_users",
    },
    allow_channels=False,
)
async def bot_users_(message: Message):
    """Usuários que iniciaram seu bot por - /start"""
    msg = ""
    async for c in BOT_START.find():
        msg += (
            f"• <i>ID:</i> <code>{c['user_id']}</code>\n   "
            f"<b>Nome:</b> {c['firstname']},  <b>Data:</b> `{c['date']}`\n"
        )
    await message.edit_or_send_as_file(
        f"<u><i><b>Bot PM Userlist</b></i></u>\n\n{msg}"
        if msg
        else "`Ninguém faz melhor`"
    )


@kannax.on_cmd(
    "bot_antif",
    about={
        "header": "ativar/desativar o Antiflood de bot",
        "description": "Seja notificado se um usuário enviar spam para seu bot e até mesmo autobans",
    },
    allow_channels=False,
)
async def bot_antiflood_(message: Message):
    """ativar/desativar o Antiflood de bot"""
    if Config.BOT_ANTIFLOOD:
        Config.BOT_ANTIFLOOD = False
        await message.edit("`Antiflood de bot desativado !`", del_in=3)
    else:
        Config.BOT_ANTIFLOOD = True
        await message.edit("`Antiflood de bot ativado!`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {"_id": "BOT_ANTIFLOOD"},
        {"$set": {"data": Config.BOT_ANTIFLOOD}},
        upsert=True,
    )
