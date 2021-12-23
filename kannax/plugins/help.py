import os
import re
import requests
import base64

from math import ceil
from typing import Any, Callable, Dict, List, Union
from random import choice
import ujson
from html_telegraph_poster import TelegraphPoster
from pyrogram import filters
from pyrogram.errors import BadRequest, MessageIdInvalid, MessageNotModified
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultAnimation,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)
from youtubesearchpython import VideosSearch

from kannax import Config, Message, get_collection, kannax
from kannax.core.ext import RawClient
from kannax.utils import get_file_id, get_response
from kannax.utils import parse_buttons as pb
from kannax.utils import rand_key

from .bot.ialive import Bot_Alive
from .bot.utube_inline import (
    download_button,
    get_yt_video_id,
    get_ytthumb,
    result_formatter,
    ytsearch_data,
)
from .fun.stylish import Styled, font_gen
from .misc.redditdl import reddit_thumb_link
from .utils.notes import get_inote

CHANNEL = kannax.getCLogger(__name__)

_CATEGORY = {
    "admin": "🔹",
    "fun": "🔹",
    "misc": "🔹",
    "tools": "🔹",
    "utils": "🔹",
    "xtra": "🔹",
    "temp": "🔹",
    "plugins": "🔹",
    "bot": "🔹",
    "custom": "🔹",
    "kawaii": "🔹",
}
# Database
SAVED_SETTINGS = get_collection("CONFIGS")
REPO_X = InlineQueryResultArticle(
    title="Repo",
    input_message_content=InputTextMessageContent(
        "**Repositorio e ultilitarios do KannaX**"),
    url="https://github.com/fnixdev/Kanna-X",
    description="Configure o seu próprio",
    thumb_url="https://telegra.ph//file/c6d95e3f661dc15bf0df7.jpg",
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✨ Repo", url="https://github.com/fnixdev/Kanna-X"),
                InlineKeyboardButton(
                    "📦 Instalar", url="https://heroku.com/deploy?template=https://github.com/fnixdev/kxinstall"),
            ],
        ]
    )
)

media_, alive_media, media_type = None, None, None


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({"_id": "CURRENT_CLIENT"})
    if data:
        Config.USE_USER_FOR_CLIENT_CHECKS = bool(data["is_user"])
    media_ = await SAVED_SETTINGS.find_one({"_id": "ALIVE_MEDIA"})
    if media_:
        Config.NEW_ALIVE_MEDIA = media_["url"]
        Config.ALIVE_MEDIA_TYPE = media_["type"]
    else:
        Config.NEW_ALIVE_MEDIA = "https://telegra.ph/file/4e956ef52c931570fb110.png"
        Config.ALIVE_MEDIA_TYPE = "photo"


@kannax.on_cmd(
    "help", about={"header": "Guia para usar os comandos KannaX"}, allow_channels=False
)
async def helpme(message: Message) -> None:
    plugins = kannax.manager.enabled_plugins
    if not message.input_str:
        out_str = (
            f"""⚒ <b><u>(<code>{len(plugins)}</code>) Plugin(s) Disponivel</u></b>\n\n"""
        )
        cat_plugins = kannax.manager.get_plugins()
        for cat in sorted(cat_plugins):
            if cat == "plugins":
                continue
            out_str += (
                f"    {_CATEGORY.get(cat, '📁')} <b>{cat}</b> "
                f"(<code>{len(cat_plugins[cat])}</code>) :   <code>"
                + "</code>    <code>".join(sorted(cat_plugins[cat]))
                + "</code>\n\n"
            )
        out_str += (
            f"""📕 <mb>Uso:</b>  <code>{Config.CMD_TRIGGER}help [nome do plugin]</code>"""
        )
    else:
        key = message.input_str
        if (
            not key.startswith(Config.CMD_TRIGGER)
            and key in plugins
            and (
                len(plugins[key].enabled_commands) > 1
                or plugins[key].enabled_commands[0].name.lstrip(Config.CMD_TRIGGER)
                != key
            )
        ):
            commands = plugins[key].enabled_commands
            out_str = f"""<b><u>(<code>{len(commands)}</code>) Comando(s)</u></b>

<b>Plugin:</b>  <code>{key}</code>
<b>Descrição:</b>  <code>{plugins[key].doc}</code>\n\n"""
            for i, cmd in enumerate(commands, start=1):
                out_str += (
                    f"    ▪️ <b>cmd:</b>  <code>{cmd.name}</code>\n"
                    f"    ▪️ <b>info:</b>  <i>{cmd.doc}</i>\n\n"
                )
            out_str += f"""📕 <b>Uso:</b>  <code>{Config.CMD_TRIGGER}help [nome do comando]</code>"""
        else:
            commands = kannax.manager.enabled_commands
            key = key.lstrip(Config.CMD_TRIGGER)
            key_ = Config.CMD_TRIGGER + key
            if key in commands:
                out_str = f"<code>{key}</code>\n\n{commands[key].about}"
            elif key_ in commands:
                out_str = f"<code>{key_}</code>\n\n{commands[key_].about}"
            else:
                out_str = f"<i>Nenhum módulo ou comando encontrado para</i>: <code>{message.input_str}</code>"
    await message.edit(
        out_str, del_in=0, parse_mode="html", disable_web_page_preview=True
    )


if kannax.has_bot:

    def check_owner(func):
        async def wrapper(_, c_q: CallbackQuery):
            if c_q.from_user and (
                c_q.from_user.id
                in Config.OWNER_ID
                # or c_q.from_user.id in Config.SUDO_USERS
            ):
                await c_q.answer()
                try:
                    await func(c_q)
                except MessageNotModified:
                    await c_q.answer("Nada foi encontrado para atualizar 🤷‍♂️", show_alert=True)
                except MessageIdInvalid:
                    await c_q.answer(
                        "Não tenho permissão para editar isto 😔",
                        show_alert=True,
                    )
            else:
                user_dict = await kannax.bot.get_user_dict(Config.OWNER_ID[0])
                await c_q.answer(
                    f"Apenas {user_dict['flname']} Pode acessar isso ...! Instale o KannaX",
                    show_alert=True,
                )

        return wrapper

    @kannax.bot.on_callback_query(
        filters.regex(pattern=r"\((.+)\)(next|prev)\((\d+)\)")
    )
    @check_owner
    async def callback_next_prev(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        n_or_p = str(callback_query.matches[0].group(2))
        p_num = int(callback_query.matches[0].group(3))
        p_num = p_num + 1 if n_or_p == "next" else p_num - 1
        pos_list = cur_pos.split("|")
        if len(pos_list) == 1:
            buttons = parse_buttons(
                p_num,
                cur_pos,
                lambda x: f"{_CATEGORY.get(x, '📁')} {x}",
                kannax.manager.get_all_plugins(),
            )
        elif len(pos_list) == 2:
            buttons = parse_buttons(
                p_num,
                cur_pos,
                lambda x: f"🔹 {x}",
                kannax.manager.get_all_plugins()[pos_list[-1]],
            )
        elif len(pos_list) == 3:
            _, buttons = plugin_data(cur_pos, p_num)
        await callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"back\((.+)\)"))
    @check_owner
    async def callback_back(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 1:
            await callback_query.answer("you are in main menu", show_alert=True)
            return
        if len(pos_list) == 2:
            text = " 𝐤𝐚𝐧𝐧𝐚𝐱 𝐦𝐞𝐧𝐮 "
            buttons = main_menu_buttons()
        elif len(pos_list) == 3:
            text, buttons = category_data(cur_pos)
        elif len(pos_list) == 4:
            text, buttons = plugin_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"enter\((.+)\)"))
    @check_owner
    async def callback_enter(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 2:
            text, buttons = category_data(cur_pos)
        elif len(pos_list) == 3:
            text, buttons = plugin_data(cur_pos)
        elif len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    @kannax.bot.on_callback_query(
        filters.regex(pattern=r"((?:un)?load|(?:en|dis)able)\((.+)\)")
    )
    @check_owner
    async def callback_manage(callback_query: CallbackQuery):
        task = str(callback_query.matches[0].group(1))
        cur_pos = str(callback_query.matches[0].group(2))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 4:
            if is_filter(pos_list[-1]):
                flt = kannax.manager.filters[pos_list[-1]]
            else:
                flt = kannax.manager.commands[pos_list[-1]]
            await getattr(flt, task)()
            text, buttons = filter_data(cur_pos)
        else:
            plg = kannax.manager.plugins[pos_list[-1]]
            await getattr(plg, task)()
            text, buttons = plugin_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^mm$"))
    @check_owner
    async def callback_mm(callback_query: CallbackQuery):
        await callback_query.edit_message_text(
            " 𝐤𝐚𝐧𝐧𝐚𝐱 𝐦𝐞𝐧𝐮 ",
            reply_markup=InlineKeyboardMarkup(main_menu_buttons()),
        )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^chgclnt$"))
    @check_owner
    async def callback_chgclnt(callback_query: CallbackQuery):
        if not RawClient.DUAL_MODE:
            return await callback_query.answer(
                "você está usando [BOT MODE], não pode mudar o cliente.", show_alert=True
            )
        if Config.USE_USER_FOR_CLIENT_CHECKS:
            Config.USE_USER_FOR_CLIENT_CHECKS = False
        elif RawClient.DUAL_MODE:
            Config.USE_USER_FOR_CLIENT_CHECKS = True
        await SAVED_SETTINGS.update_one(
            {"_id": "CURRENT_CLIENT"},
            {"$set": {"is_user": Config.USE_USER_FOR_CLIENT_CHECKS}},
            upsert=True,
        )
        await callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(main_menu_buttons())
        )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"refresh\((.+)\)"))
    @check_owner
    async def callback_exit(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)
        else:
            text, buttons = plugin_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    def is_filter(name: str) -> bool:
        split_ = name.split(".")
        return bool(split_[0] and len(split_) == 2)

    def parse_buttons(
        page_num: int,
        cur_pos: str,
        func: Callable[[str], str],
        data: Union[List[str], Dict[str, Any]],
        rows: int = 5,
    ):
        buttons = [
            InlineKeyboardButton(
                func(x), callback_data=f"enter({cur_pos}|{x})".encode()
            )
            for x in sorted(data)
        ]
        pairs = list(map(list, zip(buttons[::2], buttons[1::2])))
        if len(buttons) % 2 == 1:
            pairs.append([buttons[-1]])
        max_pages = ceil(len(pairs) / rows)
        current_page = page_num % max_pages
        if len(pairs) > rows:
            pairs = pairs[current_page * rows: (current_page + 1) * rows] + [
                [
                    InlineKeyboardButton(
                        "⏪ Anterior",
                        callback_data=f"({cur_pos})prev({current_page})".encode(
                        ),
                    ),
                    InlineKeyboardButton(
                        "⏩ Proximo",
                        callback_data=f"({cur_pos})next({current_page})".encode(
                        ),
                    ),
                ],
            ]
        pairs += default_buttons(cur_pos)
        return pairs

    def main_menu_buttons():
        return parse_buttons(
            0,
            "mm",
            lambda x: f"{_CATEGORY.get(x, '📁')} {x}",
            kannax.manager.get_all_plugins(),
        )

    def default_buttons(cur_pos: str):
        tmp_btns = []
        if cur_pos != "mm":
            tmp_btns.append(
                InlineKeyboardButton(
                    "⬅ Voltar", callback_data=f"back({cur_pos})".encode()
                )
            )
            if len(cur_pos.split("|")) > 2:
                tmp_btns.append(InlineKeyboardButton(
                    "🖥 Menu Principal", callback_data="mm"))
                tmp_btns.append(
                    InlineKeyboardButton(
                        "🔄 Atualizar", callback_data=f"refresh({cur_pos})".encode()
                    )
                )
        else:
            cur_clnt = "👤 USER" if Config.USE_USER_FOR_CLIENT_CHECKS else "⚙️ BOT"
            tmp_btns.append(
                InlineKeyboardButton(
                    f"🔩 Client para Checks e Sudos : {cur_clnt}",
                    callback_data="chgclnt",
                )
            )
        return [tmp_btns]

    def category_data(cur_pos: str):
        pos_list = cur_pos.split("|")
        plugins = kannax.manager.get_all_plugins()[pos_list[1]]
        text = (
            f"**(`{len(plugins)}`) Plugin(s) Under : "
            f"`{_CATEGORY.get(pos_list[1], '📁')} {pos_list[1]}`  Categoria**"
        )
        buttons = parse_buttons(0, "|".join(
            pos_list[:2]), lambda x: f"🔹 {x}", plugins)
        return text, buttons

    def plugin_data(cur_pos: str, p_num: int = 0):
        pos_list = cur_pos.split("|")
        plg = kannax.manager.plugins[pos_list[2]]
        text = f"""🔹 <u><b>Plugin Status<b></u> 🔹

🎭 **Categoria** : `{pos_list[1]}`
🔖 **Nome** : `{plg.name}`
📝 **Doc** : `{plg.doc}`
◾️ **Comandos** : `{len(plg.commands)}`
⚖ **Filters** : `{len(plg.filters)}`
✅ **Carregado** : `{plg.is_loaded}`
➕ **Habilitado** : `{plg.is_enabled}`
"""
        tmp_btns = []
        if plg.is_loaded:
            tmp_btns.append(
                InlineKeyboardButton(
                    "❎ Descarregar",
                    callback_data=f"unload({'|'.join(pos_list[:3])})".encode(),
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "✅ Carregar", callback_data=f"load({'|'.join(pos_list[:3])})".encode()
                )
            )
        if plg.is_enabled:
            tmp_btns.append(
                InlineKeyboardButton(
                    "➖ Desativar",
                    callback_data=f"disable({'|'.join(pos_list[:3])})".encode(
                    ),
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "➕ Habilitar",
                    callback_data=f"enable({'|'.join(pos_list[:3])})".encode(),
                )
            )
        buttons = parse_buttons(
            p_num,
            "|".join(pos_list[:3]),
            lambda x: f"⚖ {x}" if is_filter(x) else f" {x}",
            (flt.name for flt in plg.commands + plg.filters),
        )
        buttons = buttons[:-1] + [tmp_btns] + [buttons[-1]]
        return text, buttons

    def filter_data(cur_pos: str):
        pos_list = cur_pos.split("|")
        plg = kannax.manager.plugins[pos_list[2]]
        flts = {flt.name: flt for flt in plg.commands + plg.filters}
        flt = flts[pos_list[-1]]
        flt_data = f"""
🔖 **Nome** : `{flt.name}`
📝 **Doc** : `{flt.doc}`
🤖 **Via Bot** : `{flt.allow_via_bot}`
✅ **Carregado** : `{flt.is_loaded}`
➕ **Habilitado** : `{flt.is_enabled}`"""
        if hasattr(flt, "about"):
            text = f"""<b><u>Status do Comando</u></b>
{flt_data}
{flt.about}
"""
        else:
            text = f"""⚖ <b><u>Status do filtro</u></b> ⚖
{flt_data}
"""
        buttons = default_buttons(cur_pos)
        tmp_btns = []
        if flt.is_loaded:
            tmp_btns.append(
                InlineKeyboardButton(
                    "❎ Descarregar", callback_data=f"unload({cur_pos})".encode()
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "✅ Carregar", callback_data=f"load({cur_pos})".encode()
                )
            )
        if flt.is_enabled:
            tmp_btns.append(
                InlineKeyboardButton(
                    "➖ Desativar", callback_data=f"disable({cur_pos})".encode()
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "➕ Habilitar", callback_data=f"enable({cur_pos})".encode()
                )
            )
        buttons = [tmp_btns] + buttons
        return text, buttons

    @kannax.bot.on_inline_query()
    async def inline_answer(_, inline_query: InlineQuery):
        results = []
        i_q = inline_query.query
        string = i_q.lower()  # All lower
        str_x = i_q.split(" ", 2)  # trigger @username Text
        str_y = i_q.split(" ", 1)  # trigger and Text
        string_split = string.split()  # All lower and Split each word
        iq_user_id = inline_query.from_user.id
        if (
            (iq_user_id in Config.OWNER_ID)
            or (iq_user_id in Config.SUDO_USERS)
            and Config.SUDO_ENABLED
        ):

            if string == "fnix":
                owner = [
                    [
                        InlineKeyboardButton(
                            text="🧙🏻‍♂️  ᴄᴏɴᴛᴀᴛᴏ", url="https://t.me/fnixdev"),
                        InlineKeyboardButton(
                            text="💭  sᴛᴀᴛᴜs", callback_data="status_alive"),
                    ]
                ]
                results.append(
                    InlineQueryResultPhoto(
                        photo_url="https://telegra.ph/file/0b88699cba8863ce42541.jpg",
                        caption="I am fnix, 21y pynto dev",
                        reply_markup=InlineKeyboardMarkup(owner),
                    )
                )

            if string == "age_verification_alert":
                buttons = [
                    [
                        InlineKeyboardButton(
                            text="Sim, tenho mais de 18 anos", callback_data="age_verification_true"
                        ),
                        InlineKeyboardButton(
                            text="Não, eu não sou", callback_data="age_verification_false"
                        ),
                    ]
                ]
                results.append(
                    InlineQueryResultPhoto(
                        photo_url="https://telegra.ph/file/93c720cb55da5b0d6767c.png",
                        caption="**VOCÊ ESTÁ VELHO O SUFICIENTE PARA ISSO?**",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if str_y[0] == "reddit":
                reddit_api = "https://meme-api.herokuapp.com/gimme/"
                if len(str_y) == 2:
                    subreddit_regex = r"^([a-zA-Z]+)\.$"
                    match = re.search(subreddit_regex, str_y[1])
                    if match:
                        subreddit_name = match.group(1)
                        reddit_api += f"{subreddit_name}/30"
                    else:
                        return
                else:
                    reddit_api += "30"
                try:
                    r = await get_response.json(reddit_api)
                except ValueError:
                    results.append(
                        InlineQueryResultArticle(
                            title="Reddit Api está desativado!",
                            input_message_content=InputTextMessageContent(
                                "**Código de erro: Status != 200**"
                            ),
                            thumb_url="https://i.imgur.com/7a7aPVa.png",
                        )
                    )
                else:
                    if "code" in r:
                        bool_is_gallery = False
                        code = r["code"]
                        code_message = r["message"]
                        results.append(
                            InlineQueryResultArticle(
                                title=str(code),
                                input_message_content=InputTextMessageContent(
                                    f"**Error Code: {code}**\n`{code_message}`"
                                ),
                                description="Digite um nome de subreddit válido!",
                                thumb_url="https://i.imgur.com/7a7aPVa.png",
                            )
                        )
                    else:
                        bool_is_gallery = True
                        for post in r["memes"]:
                            if "url" in post:
                                postlink = post["postLink"]
                                subreddit = post["subreddit"]
                                title = post["title"]
                                media_url = post["url"]
                                author = post["author"]
                                upvote = post["ups"]
                                captionx = f"<b>{title}</b>\n"
                                captionx += f"`Posted by u/{author}`\n"
                                captionx += f"↕️ <code>{upvote}</code>\n"
                                thumbnail = reddit_thumb_link(post["preview"])
                                if post["spoiler"]:
                                    captionx += "⚠️ Post marcado como SPOILER\n"
                                if post["nsfw"]:
                                    captionx += "🔞 Post marcado como Adulto \n"
                                buttons = [
                                    [
                                        InlineKeyboardButton(
                                            f"Fonte: r/{subreddit}", url=postlink
                                        )
                                    ]
                                ]
                                if media_url.endswith(".gif"):
                                    results.append(
                                        InlineQueryResultAnimation(
                                            animation_url=media_url,
                                            thumb_url=thumbnail,
                                            caption=captionx,
                                            reply_markup=InlineKeyboardMarkup(
                                                buttons),
                                        )
                                    )
                                else:
                                    results.append(
                                        InlineQueryResultPhoto(
                                            photo_url=media_url,
                                            thumb_url=thumbnail,
                                            caption=captionx,
                                            reply_markup=InlineKeyboardMarkup(
                                                buttons),
                                        )
                                    )
                    await inline_query.answer(
                        results=results,
                        cache_time=1,
                        is_gallery=bool_is_gallery,
                        switch_pm_text="Comandos Disponíveis",
                        switch_pm_parameter="inline",
                    )
                    return

            if string == "alive":
                me = await kannax.get_me()
                alive_info = await Bot_Alive.alive_info()
                buttons = Bot_Alive.alive_buttons()
                if Config.ALIVE_MEDIA_TYPE == "photo":
                    results.append(
                        InlineQueryResultPhoto(
                            photo_url=Config.NEW_ALIVE_MEDIA,
                            caption=alive_info,
                            reply_markup=buttons,
                        )
                    )
                elif Config.ALIVE_MEDIA_TYPE == "gif" or "video":
                    results.append(
                        InlineQueryResultAnimation(
                            animation_url=Config.NEW_ALIVE_MEDIA,
                            caption=alive_info,
                            reply_markup=buttons,
                        )
                    )

            if string == "geass":
                results.append(
                    InlineQueryResultAnimation(
                        animation_url="https://telegra.ph/file/7b2cca848cc29586bd70b.png",
                        caption="Para derrotar o mal, devo me tornar um mal maior",
                    )
                )

            if str_y[0] == "inotes" and len(str_y) == 2:
                note_data = str_y[1].split("_", 2)
                note_data = [int(x) for x in note_data]
                if len(note_data) == 3:
                    cnote = await get_inote(
                        note_id=note_data[0], chat_id=note_data[1], user_id=note_data[2]
                    )
                    type_ = cnote.get("type")
                    if type_ == "image":
                        results.append(
                            InlineQueryResultCachedPhoto(
                                file_id=cnote.get("file_id"),
                                caption=cnote.get("caption"),
                                reply_markup=cnote.get("buttons"),
                            )
                        )
                    elif type_ == "media":
                        results.append(
                            InlineQueryResultCachedDocument(
                                title="Inline Note",
                                file_id=cnote.get("file_id"),
                                caption=cnote.get("caption"),
                                description=f"#{note_data[0]}",
                                reply_markup=cnote.get("buttons"),
                            )
                        )
                    else:
                        results.append(
                            InlineQueryResultArticle(
                                title="Inline Note",
                                input_message_content=InputTextMessageContent(
                                    cnote.get("caption"), disable_web_page_preview=True
                                ),
                                description=f"#{note_data[0]}",
                                reply_markup=cnote.get("buttons"),
                            )
                        )

            if string == "gapps":
                buttons = [
                    [
                        InlineKeyboardButton(
                            "Flame GApps", callback_data="flame_gapps"),
                        InlineKeyboardButton(
                            "Weeb Gapps", callback_data="weeb_gapps"),
                    ],
                    [
                        InlineKeyboardButton(
                            "Nik GApps", callback_data="nik_gapps"),
                        InlineKeyboardButton(
                            "Bit GApps", callback_data="bit_gapps"),
                    ],
                    [
                        InlineKeyboardButton(
                            "Lite Gapps", callback_data="lite_gapps")
                    ],
                ]
                results.append(
                    InlineQueryResultArticle(
                        title="GApps",
                        input_message_content=InputTextMessageContent(
                            "[\u200c](https://i.imgur.com/BZBMrfn.jpg) **Ultimos Gapps arm64 Android 11**"
                        ),
                        description="Obtenha os links de download mais recentes do GApps",
                        thumb_url="https://i.imgur.com/Npzw8Ph.png",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if len(string_split) == 2 and (string_split[0] == "ofox"):
                codename = string_split[1]
                t = TelegraphPoster(use_api=True)
                t.create_api_token("KannaX")
                photo = "https://i.imgur.com/582uaSk.png"
                api_host = "https://api.orangefox.download/v2/device/"
                try:
                    async with get_response.get_session() as session:
                        r = await get_response.json(
                            f"{api_host}{codename}", session=session
                        )
                        s = await get_response.json(
                            f"{api_host}{codename}/releases/stable/last",
                            session=session,
                        )
                except ValueError:
                    return
                info = f"📱 **Device**: {r['fullname']}\n"
                info += f"👤 **Maintainer**: {r['maintainer']['name']}\n\n"
                recovery = f"🦊 <code>{s['file_name']}</code>\n"
                recovery += f"📅 {s['date']}\n"
                recovery += f"ℹ️ **Version:** {s['version']}\n"
                recovery += f"📌 **Build Type:** {s['build_type']}\n"
                recovery += f"🔰 **Size:** {s['size_human']}\n\n"
                recovery += "📍 **Changelog:**\n"
                recovery += f"<code>{s['changelog']}</code>\n\n"
                msg = info
                msg += recovery
                notes_ = s.get("notes")
                if notes_:
                    notes = t.post(title="READ Notes", author="", text=notes_)
                    buttons = [
                        [
                            InlineKeyboardButton("🗒️ NOTES", url=notes["url"]),
                            InlineKeyboardButton("⬇️ DOWNLOAD", url=s["url"]),
                        ]
                    ]
                else:
                    buttons = [[InlineKeyboardButton(
                        text="⬇️ DOWNLOAD", url=s["url"])]]
                results.append(
                    InlineQueryResultPhoto(
                        photo_url=photo,
                        thumb_url="https://i.imgur.com/o0onLYB.jpg",
                        title="Latest OFOX RECOVERY",
                        description=f"For device : {codename}",
                        caption=msg,
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

# REPO
            if string == "repo":
                buttons = [
                    [
                        InlineKeyboardButton(
                            "✨ Repo", url="https://github.com/fnixdev/Kanna-X"),
                        InlineKeyboardButton(
                            "📦 Instalar", url="https://heroku.com/deploy?template=https://github.com/fnixdev/kxinstall"),
                    ],
                ]
                results.append(
                    InlineQueryResultPhoto(
                        title="Repo",
                        thumb_url="https://telegra.ph//file/c6d95e3f661dc15bf0df7.jpg",
                        photo_url="https://telegra.ph/file/067bf96031b0588652a82.png",
                        caption="**Repositorio e ultilitarios do KannaX**",
                        description="Configure o seu próprio",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )
# String Session
            if string == "session":
                buttons = [
                    [
                        InlineKeyboardButton(
                            "REPL", url="https://replit.com/@fnixdev/StringSessionKX"),
                        InlineKeyboardButton(
                            "Pyrogram Bot", url="https://t.me/genStr_Bot"),
                    ],
                ]
                results.append(
                    InlineQueryResultPhoto(
                        title="Session",
                        thumb_url="https://telegra.ph//file/c6d95e3f661dc15bf0df7.jpg",
                        photo_url="https://telegra.ph/file/067bf96031b0588652a82.png",
                        caption="**Gere sua SessionString pyrogram**",
                        description="Session String",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )
# Cotações
            if string == "cota":
                buttons = [
                    [
                        InlineKeyboardButton(
                            "Moedas Internacionais", callback_data="moeda_internacionais"),
                        InlineKeyboardButton(
                            "Crypto Moedas", callback_data="crypto_moedas"),
                    ],
                ]
                results.append(
                    InlineQueryResultPhoto(
                        title="Session",
                        thumb_url="https://telegra.ph/file/d30ce8f435c85406114f7.png",
                        photo_url="https://telegra.ph/file/d30ce8f435c85406114f7.png",
                        caption="**Mostra a cotação das moedas atualmente**",
                        description="Moedas",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if str_y[0] == "spoiler":
                if not os.path.exists(f"{Config.CACHE_PATH}/spoiler_db.json"):
                    results.append(
                        InlineQueryResultArticle(
                            title="Nenhum spoiler encontrado",
                            input_message_content=InputTextMessageContent(
                                "Nenhum spoiler encontrado !\nVamos adicionar alguns 😈"
                            ),
                            description="Veja .help para mais informações",
                        )
                    )
                else:
                    bot_name = (await kannax.bot.get_me()).username
                    if len(str_y) == 2:
                        link = f"https://t.me/{bot_name}?start=spoiler_{str_y[1]}"
                        buttons = [
                            [InlineKeyboardButton(
                                text="Ver Spoiler", url=link)]
                        ]
                        results.append(
                            InlineQueryResultArticle(
                                title="Spoiler",
                                input_message_content=InputTextMessageContent(
                                    "<b>Clique para ver o spoiler !</b>"
                                ),
                                description="Clique para enviar",
                                thumb_url="https://telegra.ph/file/ee3a6439494463acd1a3a.jpg",
                                reply_markup=InlineKeyboardMarkup(buttons),
                            )
                        )
                    else:
                        fo = open(f"{Config.CACHE_PATH}/spoiler_db.json")
                        view_db = ujson.load(fo)
                        fo.close()
                        if len(view_db) != 0:
                            for numm, spoilerr in enumerate(view_db, start=1):
                                buttons = [
                                    [
                                        InlineKeyboardButton(
                                            text="Ver Spoiler",
                                            url=f"https://t.me/{bot_name}?start=spoiler_{spoilerr}",
                                        )
                                    ]
                                ]
                                saved_at = view_db.get(spoilerr, None)
                                savetime = (
                                    saved_at.get(
                                        "savetime", None) if saved_at else None
                                )
                                results.append(
                                    InlineQueryResultArticle(
                                        title=f"#{numm}  Spoiler",
                                        input_message_content=InputTextMessageContent(
                                            "<b>Clique para ver o spoiler !</b>"
                                        ),
                                        description=f"Criado em: {savetime}",
                                        thumb_url="https://telegra.ph/file/ee3a6439494463acd1a3a.jpg",
                                        reply_markup=InlineKeyboardMarkup(
                                            buttons),
                                    )
                                )

            if str_x[0].lower() == "op" and len(str_x) > 1:
                txt = i_q[3:]
                opinion = os.path.join(Config.CACHE_PATH, "emoji_data.txt")
                if os.path.exists(opinion):
                    with open(opinion) as fo:
                        view_data = ujson.load(fo)
                    # Uniquely identifies an inline message
                    new_id = {int(inline_query.id): [{}]}
                    view_data.update(new_id)
                else:
                    view_data = {int(inline_query.id): [{}]}
                with open(opinion, "w") as outfile:
                    ujson.dump(view_data, outfile)
                buttons = [
                    [
                        InlineKeyboardButton(
                            "👍", callback_data=f"op_y_{inline_query.id}"
                        ),
                        InlineKeyboardButton(
                            "👎", callback_data=f"op_n_{inline_query.id}"
                        ),
                    ]
                ]
                results.append(
                    InlineQueryResultArticle(
                        title="Ask For Opinion",
                        input_message_content=InputTextMessageContent(txt),
                        description=f"Q. {txt}",
                        thumb_url="https://i.imgur.com/Zlc98qS.jpg",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if "btn_" in str_y[0] or str_y[0] == "btn":
                inline_db_path = f"{Config.CACHE_PATH}/inline_db.json"
                if os.path.exists(inline_db_path):
                    with open(inline_db_path, "r") as data_file:
                        view_db = ujson.load(data_file)
                    data_count_n = 1
                    reverse_list = list(view_db)
                    reverse_list.reverse()
                    for butt_ons in reverse_list:
                        if data_count_n > 30:
                            view_db.pop(butt_ons, None)
                        data_count_n += 1
                    with open(inline_db_path, "w") as data_file:
                        ujson.dump(view_db, data_file)
                    if str_y[0] == "btn":
                        inline_storage = list(view_db)
                    else:
                        rnd_id = (str_y[0].split("_", 1))[1]
                        inline_storage = [rnd_id]
                    if len(inline_storage) == 0:
                        return
                    for inline_content in inline_storage:
                        inline_db = view_db.get(inline_content)
                        if inline_db:
                            if (
                                inline_db["media_valid"]
                                and int(inline_db["media_id"]) != 0
                            ):
                                saved_msg = await kannax.bot.get_messages(
                                    Config.LOG_CHANNEL_ID, int(
                                        inline_db["media_id"])
                                )
                                media_data = get_file_id(saved_msg)
                            textx, buttonsx = pb(inline_db["msg_content"])
                            if inline_db["media_valid"]:
                                if saved_msg.photo:
                                    results.append(
                                        InlineQueryResultCachedPhoto(
                                            file_id=media_data,
                                            caption=textx,
                                            reply_markup=buttonsx,
                                        )
                                    )
                                else:
                                    results.append(
                                        InlineQueryResultCachedDocument(
                                            title=textx,
                                            file_id=media_data,
                                            caption=textx,
                                            description="Inline Button",
                                            reply_markup=buttonsx,
                                        )
                                    )
                            else:
                                results.append(
                                    InlineQueryResultArticle(
                                        title=textx,
                                        input_message_content=InputTextMessageContent(
                                            textx
                                        ),
                                        reply_markup=buttonsx,
                                    )
                                )

            if str_y[0].lower() == "stylish" and len(str_y) == 2:
                results = []
                for f_name in Styled.font_choice:
                    styled_str = font_gen(f_name, str_y[1])
                    results.append(
                        InlineQueryResultArticle(
                            title=f_name.upper(),
                            input_message_content=InputTextMessageContent(
                                f"`{styled_str}`"
                            ),
                            description=styled_str,
                        )
                    )
                await inline_query.answer(
                    results=results,
                    cache_time=1,
                    switch_pm_text="Comandos Disponiveis",
                    switch_pm_parameter="inline",
                )
                return


            if str_x[0].lower() in ["secret", "troll"] and len(str_x) == 3:
                user_name = str_x[1]
                msg = str_x[2]
                try:
                    receiver = await kannax.get_users(user_name)
                except (BadRequest, IndexError):
                    return
                secret = os.path.join(Config.CACHE_PATH, "secret.json")
                key_ = rand_key()
                r_name = (
                    ("@" + receiver.username)
                    if receiver.username
                    else f"{receiver.first_name} {receiver.last_name or ''}"
                )
                secret_data = {
                    key_: {
                        "sender": iq_user_id,
                        "receiver": {"id": receiver.id, "name": r_name},
                        "msg": msg,
                        "views": [],
                    }
                }
                if os.path.exists(secret):
                    with open(secret) as outfile:
                        view_data = ujson.load(outfile)
                    view_data.update(secret_data)
                else:
                    view_data = secret_data
                # Save
                with open(secret, "w") as r:
                    ujson.dump(view_data, r, indent=4)
                if str_x[0].lower() == "secret":
                    c_data = f"secret_{key_}"
                    i_m_content = f"📩 <b>Mensagem Secreta</b> para <b>{r_name}</b>. Só ele/ela pode abrir."
                    i_l_des = f"Enviar mensagem secreta para: {r_name}"
                    title = "Enviar mensagem secreta"
                    thumb_img = "https://telegra.ph/file/8db040d03e6c5ba2cfd08.png"
                else:
                    c_data = f"troll_{key_}"
                    i_m_content = f"😈 Apenas <b>{r_name}</b> não pode ver esta mensagem. UwU"
                    i_l_des = f"Mensagem Oculta de {r_name}"
                    title = "😈 Troll"
                    thumb_img = "https://i.imgur.com/0vg5B0A.png"
                buttons = [[InlineKeyboardButton(
                    "🔐  Mostrar", callback_data=c_data)]]
                results.append(
                    InlineQueryResultArticle(
                        title=title,
                        input_message_content=InputTextMessageContent(
                            i_m_content),
                        description=i_l_des,
                        thumb_url=thumb_img,
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if str_y[0].lower() == "ytdl" and len(str_y) == 2:
                link = get_yt_video_id(str_y[1].strip())
                found_ = True
                if link is None:
                    search = VideosSearch(str_y[1].strip(), limit=15)
                    resp = (search.result()).get("result")
                    if len(resp) == 0:
                        found_ = False
                    else:
                        outdata = await result_formatter(resp)
                        key_ = rand_key()
                        ytsearch_data.store_(key_, outdata)
                        buttons = InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text=f"1 / {len(outdata)}",
                                        callback_data=f"ytdl_next_{key_}_1",
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        text="📜  List all",
                                        callback_data=f"ytdl_listall_{key_}_1",
                                    ),
                                    InlineKeyboardButton(
                                        text="⬇️  Download",
                                        callback_data=f'ytdl_download_{outdata[1]["video_id"]}_0',
                                    ),
                                ],
                            ]
                        )
                        caption = outdata[1]["message"]
                        photo = outdata[1]["thumb"]
                else:
                    caption, buttons = await download_button(link, body=True)
                    photo = await get_ytthumb(link)

                if found_:
                    results.append(
                        InlineQueryResultPhoto(
                            photo_url=photo,
                            title=link,
                            description="⬇️ Clique para fazer o download",
                            caption=caption,
                            reply_markup=buttons,
                        )
                    )
                else:
                    results.append(
                        InlineQueryResultArticle(
                            title="not Found",
                            input_message_content=InputTextMessageContent(
                                f"Nenhum resultado encontrado para `{str_y[1]}`"
                            ),
                            description="INVALID",
                        )
                    )

            MAIN_MENU = InlineQueryResultArticle(
                title="Abrir menu inline",
                input_message_content=InputTextMessageContent(" 𝐤𝐚𝐧𝐧𝐚𝐱 𝐦𝐞𝐧𝐮 "),
                url="https://github.com/fnixdev/Kanna-X",
                description="KannaX Menu",
                thumb_url="https://telegra.ph/file/d768df44c2d9b02e0f0ca.jpg",
                reply_markup=InlineKeyboardMarkup(main_menu_buttons()),
            )
            results.append(MAIN_MENU)
            if len(results) != 0:
                await inline_query.answer(
                    results=results,
                    cache_time=1,
                    switch_pm_text="Comandos Inline",
                    switch_pm_parameter="inline",
                )
        else:
            results.append(REPO_X)
            await inline_query.answer(
                results=results,
                cache_time=1,
                switch_pm_text=f"Apenas meu mestre pode acessar isso",
                switch_pm_parameter="start",
            )