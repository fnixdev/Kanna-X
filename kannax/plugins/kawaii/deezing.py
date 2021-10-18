# made for kannax by @Kakashi_HTK(tg)/@ashwinstr(gh)
# v2.0.1

from asyncio import gather

from kannax import Config, Message, kannax


@kannax.on_cmd(
    "dz",
    about={
        "header": "deezer music",
        "description": "baixar musicas usando @deezermusicbot",
        "usage": "{tr}dz nome da musica ou artista ; [numero](opcional)",
    },
)
async def deezing_(message: Message):
    """download music using @deezermusicbot"""
    query_ = message.input_str
    if ";" in query_:
        split_ = query_.split(";", 1)
        song_, num = split_[0].strip, split_[1].strip
    else:
        song_ = query_
        num = "0"
    if not num.isdigit():
        await message.edit("Por favor, insira um número adequado após ';'...", del_in=5)
        return
    bot_ = "deezermusicbot"
    await message.edit(f"Procurando <b>{song_}</b> no deezer...")
    results = await kannax.get_inline_bot_results(bot_, song_)
    if not results.results[0]:
        await message.edit(f"Musica <code>{song_}</code> não encontrada...", del_in=5)
        return
    try:
        log_send = await kannax.send_inline_bot_result(
            chat_id=Config.LOG_CHANNEL_ID,
            query_id=results.query_id,
            result_id=results.results[int(num)].id,
        )
        await gather(
            kannax.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.LOG_CHANNEL_ID,
                message_id=log_send.updates[0].id,
            ),
            message.delete(),
        )
    except BaseException:
        await message.err(
            "Algo inesperado aconteceu, por favor tente novamente mais tarde...", del_in=5
        )
        return
