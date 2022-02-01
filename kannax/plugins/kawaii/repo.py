# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

from kannax import Message, kannax


@kannax.on_cmd(
    "repo",
    about={
        "header": "link e detalhes do repositório",
    },
)
async def see_repo(message: Message):
    bot = await kannax.bot.get_me()
    x = await kannax.get_inline_bot_results(bot.username, "repo")
    await kannax.send_inline_bot_result(
        chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
    )
    await message.delete()


@kannax.on_cmd(
    "string",
    about={
        "header": "link e detalhes do repositório",
    },
)
async def see_session(message: Message):
    bot = await kannax.bot.get_me()
    x = await kannax.get_inline_bot_results(bot.username, "session")
    await kannax.send_inline_bot_result(
        chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
    )
    await message.delete()
