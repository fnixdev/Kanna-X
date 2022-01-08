# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.


"""Gapps via inline bot"""
import requests
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from requests import get

from kannax import Config, Message, kannax

# TODO Make Check Admin and Sudos Wrapper


@kannax.on_cmd(
    "gapps", about={"header": "Obtenha gapps arm64 11 mais recente"}, allow_channels=False
)
async def gapps_inline(message: Message):
    await message.edit("`🔍 Procurando gapps...`")
    bot = await kannax.bot.get_me()
    x = await kannax.get_inline_bot_results(bot.username, "gapps")
    await kannax.send_inline_bot_result(
        chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
    )
    await message.delete()


if kannax.has_bot:

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^bit_gapps$"))
    async def nik_cb(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            link = (
                "https://bitgapps.ga/GApps/arm64/R/BiTGApps-arm64-11.0.0-R38_signed.zip"
            )
            url = get(link)
            if url.status_code == 404:
                return
            nik_g = [
                [InlineKeyboardButton(text="Mais Recente", url=link)],
                [InlineKeyboardButton(text="⏪  VOLTAR", callback_data="back_gapps")],
            ]

            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "[\u200c](https://telegra.ph/file/7783c02112f33029a6f35.png) **BIT GAPPS**",
                reply_markup=InlineKeyboardMarkup(nik_g),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^flame_menu$"))
    async def back_cb(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton("Android 11", callback_data="flame11_gapps"),
                    InlineKeyboardButton("Android 12", callback_data="flame12_gapps"),
                ],
                [
                    InlineKeyboardButton(text="⏪  VOLTAR", callback_data="back_gapps")],
                            ]
            ]
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "[\u200c](https://telegra.ph/file/c3cdea0642e1723f3304c.jpg) **FlameGapps**",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )


    @kannax.bot.on_callback_query(filters.regex(pattern=r"^flame11_gapps$"))
    async def flame_cb(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            link = "https://sourceforge.net/projects/flamegapps/files/arm64/android-11/"
            url = get(link)
            if url.status_code == 404:
                return
            page = BeautifulSoup(url.content, "lxml")
            content = page.tbody.tr
            date = content["title"]
            date2 = date.replace("-", "")
            flame = "{link}{date}/FlameGApps-11.0-{varient}-arm64-{date2}.zip/download"
            basic = flame.format(link=link, date=date, varient="basic", date2=date2)
            full = flame.format(link=link, date=date, varient="full", date2=date2)

            flame_g = [
                [
                    InlineKeyboardButton(text="FULL", url=full),
                    InlineKeyboardButton(text="BASIC", url=basic),
                ],
                [InlineKeyboardButton(text="⏪  VOLTAR", callback_data="flame_menu")],
            ]
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "[\u200c](https://telegra.ph/file/c3cdea0642e1723f3304c.jpg)**FLAME GAPPS A11**",
                reply_markup=InlineKeyboardMarkup(flame_g),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n  ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^flame12_gapps$"))
    async def flame_cb(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            link = "https://sourceforge.net/projects/flamegapps/files/arm64/canary/android-12/"
            url = get(link)
            if url.status_code == 404:
                return
            page = BeautifulSoup(url.content, "lxml")
            content = page.tbody.tr
            date = content["title"]
            date2 = date.replace("-", "")
            flame = "{link}{date}/FlameGApps-Canary-12.0-{varient}-arm64-{date2}.zip/download"
            basic = flame.format(link=link, date=date, varient="basic", date2=date2)
            full = flame.format(link=link, date=date, varient="full", date2=date2)
            flame_g = [
                [
                    InlineKeyboardButton(text="FULL", url=full),
                    InlineKeyboardButton(text="BASIC", url=basic),
                ],
                [InlineKeyboardButton(text="⏪  VOLTAR", callback_data="flame_menu")],
            ]
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "[\u200c](https://telegra.ph/file/c3cdea0642e1723f3304c.jpg)**FLAME GAPPS A12**",
                reply_markup=InlineKeyboardMarkup(flame_g),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n  ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^nik_gapps$"))
    async def nik_cb(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            link = (
                "https://sourceforge.net/projects/nikgapps/files/Releases/NikGapps-R/"
            )
            url = get(link)
            if url.status_code == 404:
                return
            page = BeautifulSoup(url.content, "lxml")
            content = page.tbody.tr
            date = content["title"]
            latest_niks = f"{link}{date}/"
            nik_g = [
                [InlineKeyboardButton(text="Mais Recente", url=latest_niks)],
                [InlineKeyboardButton(text="⏪  VOLTAR", callback_data="back_gapps")],
            ]

            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "[\u200c](https://i.imgur.com/Iv9ZTDW.jpg) **NIK GAPPS**",
                reply_markup=InlineKeyboardMarkup(nik_g),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^weeb_gapps$"))
    async def nik_cb(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            link = (
                "https://t.me/WeebGappsChannel"
            )
            url = get(link)
            if url.status_code == 404:
                return
            nik_g = [
                [InlineKeyboardButton(text="Mais Recente", url=link)],
                [InlineKeyboardButton(text="⏪  VOLTAR", callback_data="back_gapps")],
            ]

            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "[\u200c](https://telegra.ph/file/3cae82a3a0d56f0b5fd0a.png) **WEEB GAPPS**",
                reply_markup=InlineKeyboardMarkup(nik_g),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^lite_gapps$"))
    async def nik_cb(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            link = (
                "https://t.me/LitegappsDownload"
            )
            url = get(link)
            if url.status_code == 404:
                return
            nik_g = [
                [InlineKeyboardButton(text="Mais Recente", url=link)],
                [InlineKeyboardButton(text="⏪  VOLTAR", callback_data="back_gapps")],
            ]

            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "[\u200c](https://telegra.ph/file/45bbb3da2b7ca396aa08c.png) **LITE GAPPS**",
                reply_markup=InlineKeyboardMarkup(nik_g),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^back_gapps$"))
    async def back_cb(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:

            buttons = [
                [
                    InlineKeyboardButton("Flame Gapps", callback_data="flame_"),
                    InlineKeyboardButton("Weeb Gapps", callback_data="weeb_gapps"),
                ],
                [   
                    InlineKeyboardButton("Nik Gapps", callback_data="nik_gapps"),
                    InlineKeyboardButton("Bit Gapps", callback_data="bit_gapps"),
                ],
                [
                    InlineKeyboardButton("Lite Gapps", callback_data="lite_gapps")
                    ],
            ]
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "[\u200c](https://i.imgur.com/BZBMrfn.jpg) **Ultimos Gapps arm64 Android 11**",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )
