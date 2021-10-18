# modulo de cotações de moedas
#
# by fnix@fnixdev

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from kannax import Message, Config, kannax
from kannax.utils import get_response

API = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,GBP-BRL,JPY-BRL,BTC-BRL,ETH-BRL,XRP-BRL,DOGE-BRL"


@kannax.on_cmd("cota", about={"header": "Mostra a cotação das moedas atualmente"})
async def cota_inline(message: Message):
    await message.edit("`Obtendo informações de moedas...`")
    bot = await kannax.bot.get_me()
    x = await kannax.get_inline_bot_results(bot.username, "cota")
    await kannax.send_inline_bot_result(
        chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
    )
    await message.delete()


if kannax.has_bot:

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^back_moedas$"))
    async def back_coin(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:

            buttons = [
                [
                    InlineKeyboardButton("Moedas Internacionais", callback_data="moeda_internacionais"),
                    InlineKeyboardButton("Crypto Moedas", callback_data="crypto_moedas"),
                ],
            ]

            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "**Mostra a cotação das moedas atualmente**",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )
#Moedas internacionais MainMenu
    @kannax.bot.on_callback_query(filters.regex(pattern=r"^moeda_internacionais$"))
    async def coin_int(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton("Dolar", callback_data="coin_dol"),
                    InlineKeyboardButton("Euro", callback_data="coin_eur"),
                ],
                [
                    InlineKeyboardButton("Libras", callback_data="coin_lib"),
                    InlineKeyboardButton("Iene", callback_data="coin_iene"),
                ],
                [
                    InlineKeyboardButton(
                        "Voltar", callback_data="back_moedas"),
                ]
            ]

            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "Moedas Internacionais",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

# Coin list
    @kannax.bot.on_callback_query(filters.regex(pattern=r"^coin_dol$"))
    async def coins_dol(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Voltar", callback_data="moeda_internacionais"),
                ]
            ]
            cota = await get_response.json(link=API)
            cota_ = cota["USDBRL"]
            bid_ = cota_["bid"]
            dat_ = cota_["create_date"]
            var_ = cota_["varBid"]
            por_ = cota_["pctChange"]
            texto = f"<u><b>Dolar</b></u>\n\n💵 <i>Valor:</i>` {bid_} R$`\n📆 <i>Data:</i>` {dat_}`\n\n📊 <i>Variação:</i>` {var_} R$`\n📊 <i>Porcentagem:</i>` {por_}%`"
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                texto,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^coin_eur$"))
    async def coins_eur(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Voltar", callback_data="moeda_internacionais"),
                ]
            ]
            cota = await get_response.json(link=API)
            cota_ = cota["EURBRL"]
            bid_ = cota_["bid"]
            dat_ = cota_["create_date"]
            var_ = cota_["varBid"]
            por_ = cota_["pctChange"]
            texto = f"<u><b>Euro</b></u>\n\n💵 <i>Valor:</i>` {bid_} R$`\n📆 <i>Data:</i>` {dat_}`\n\n📊 <i>Variação:</i>` {var_} R$`\n📊 <i>Porcentagem:</i>` {por_}%`"
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                texto,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^coin_lib$"))
    async def coins_lib(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Voltar", callback_data="moeda_internacionais"),
                ]
            ]
            cota = await get_response.json(link=API)
            cota_ = cota["GBPBRL"]
            bid_ = cota_["bid"]
            dat_ = cota_["create_date"]
            var_ = cota_["varBid"]
            por_ = cota_["pctChange"]
            texto = f"<u><b>Libras</b></u>\n\n💵 <i>Valor:</i>` {bid_} R$`\n📆 <i>Data:</i>` {dat_}`\n\n📊 <i>Variação:</i>` {var_} R$`\n📊 <i>Porcentagem:</i>` {por_}%`"
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                texto,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^coin_iene$"))
    async def coins_iene(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Voltar", callback_data="moeda_internacionais"),
                ]
            ]
            cota = await get_response.json(link=API)
            cota_ = cota["JPYBRL"]
            bid_ = cota_["bid"]
            dat_ = cota_["create_date"]
            var_ = cota_["varBid"]
            por_ = cota_["pctChange"]
            texto = f"<u><b>Iene Japonês</b></u>\n\n💵 <i>Valor:</i>` {bid_} R$`\n📆 <i>Data:</i>` {dat_}`\n\n📊 <i>Variação:</i>` {var_} R$`\n📊 <i>Porcentagem:</i>` {por_}%`"
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                texto,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )


#Crypto Moedas MainMenu
    @kannax.bot.on_callback_query(filters.regex(pattern=r"^crypto_moedas$"))
    async def crypto_coins(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton("Bitcoin", callback_data="crypt_btc"),
                    InlineKeyboardButton("Ethereum", callback_data="crypt_eth"),
                ],
                [
                    InlineKeyboardButton("Ripple ", callback_data="crypt_xrp"),
                    InlineKeyboardButton("Dogecoin ", callback_data="crypt_doge"),
                ],
                [
                    InlineKeyboardButton(
                        "Voltar", callback_data="back_moedas"),
                ]
            ]

            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                "Crypto Moedas",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )


#Crypto list
    @kannax.bot.on_callback_query(filters.regex(pattern=r"^crypt_btc$"))
    async def crypto_btc(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Voltar", callback_data="crypto_moedas"),
                ]
            ]
            cota = await get_response.json(link=API)
            cota_ = cota["BTCBRL"]
            bid_ = cota_["bid"]
            dat_ = cota_["create_date"]
            var_ = cota_["varBid"]
            por_ = cota_["pctChange"]
            texto = f"<u><b>Bitcoin</b></u>\n\n💵 <i>Valor:</i>` {bid_} R$`\n📆 <i>Data:</i>` {dat_}`\n\n📊 <i>Variação:</i>` {var_} R$`\n📊 <i>Porcentagem:</i>` {por_}%`"
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                texto,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^crypt_eth$"))
    async def crypto_eth(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Voltar", callback_data="crypto_moedas"),
                ]
            ]
            cota = await get_response.json(link=API)
            cota_ = cota["ETHBRL"]
            bid_ = cota_["bid"]
            dat_ = cota_["create_date"]
            var_ = cota_["varBid"]
            por_ = cota_["pctChange"]
            texto = f"<u><b>Ethereum</b></u>\n\n💵 <i>Valor:</i>` {bid_} R$`\n📆 <i>Data:</i>` {dat_}`\n\n📊 <i>Variação:</i>` {var_} R$`\n📊 <i>Porcentagem:</i>` {por_}%`"
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                texto,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^crypt_xrp$"))
    async def crypto_xrp(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Voltar", callback_data="crypto_moedas"),
                ]
            ]
            cota = await get_response.json(link=API)
            cota_ = cota["XRPBRL"]
            bid_ = cota_["bid"]
            dat_ = cota_["create_date"]
            var_ = cota_["varBid"]
            por_ = cota_["pctChange"]
            texto = f"<u><b>Ripple</b></u>\n\n💵 <i>Valor:</i>` {bid_} R$`\n📆 <i>Data:</i>` {dat_}`\n\n📊 <i>Variação:</i>` {var_} R$`\n📊 <i>Porcentagem:</i>` {por_}%`"
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                texto,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

    @kannax.bot.on_callback_query(filters.regex(pattern=r"^crypt_doge$"))
    async def crypto_doge(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id
        if u_id in Config.OWNER_ID or u_id in Config.SUDO_USERS:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Voltar", callback_data="crypto_moedas"),
                ]
            ]
            cota = await get_response.json(link=API)
            cota_ = cota["DOGEBRL"]
            bid_ = cota_["bid"]
            dat_ = cota_["create_date"]
            var_ = cota_["varBid"]
            por_ = cota_["pctChange"]
            texto = f"<u><b>Dogecoin</b></u>\n\n💵 <i>Valor:</i>` {bid_} R$`\n📆 <i>Data:</i>` {dat_}`\n\n📊 <i>Variação:</i>` {var_} R$`\n📊 <i>Porcentagem:</i>` {por_}%`"
            await kannax.bot.edit_inline_text(
                callback_query.inline_message_id,
                texto,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await callback_query.answer(
                "Desculpe, você não pode acessar isto!\n\n ɪɴsᴛᴀʟᴇ sᴇᴜ KᴀɴɴᴀX",
                show_alert=True,
            )

