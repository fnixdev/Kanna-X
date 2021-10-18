"""Bloquear/desbloquear usuário-alvo!"""

# Plugin By - XlayerCharon[XCB] X github.com/code-rgb
# TG ~>>//@CharonCB21 X //@DeletedUser420


import asyncio

from pyrogram.errors import BadRequest

from kannax import Config, Message, kannax
from kannax.utils import mention_html

CHANNEL = kannax.getCLogger(__name__)


@kannax.on_cmd(
    "block",
    about={
        "header": "Bloqueia um usuário!",
        "usage": "{tr}block [ID] ou [responda um usuario]",
        "examples": "{tr}block @fnixdev",
    },
)

async def block_user(message: Message):
    """Bloqueia um usuário!"""
    reply = message.reply_to_message
    user_id = reply.from_user.id if reply else message.input_str
    if not (reply or message.input_str):
        await message.err("Responda a um usuário ou forneça ID para bloqueá-lo !", del_in=5)
        return
    user_id = reply.from_user.id if reply else message.input_str
    bot_id = (await kannax.bot.get_me()).id
    if user_id == bot_id or user_id in Config.OWNER_ID:
        await message.edit("Você está falando sério, mano? :/")
        await asyncio.sleep(2)
        await message.edit("Você quer que eu me bloqueie? :|", del_in=5)
    elif user_id in Config.SUDO_USERS:
        await message.err("Remova o usuário do sudo primeiro", del_in=5)
    else:
        try:
            user = await kannax.get_users(user_id)
        except BadRequest:
            await message.err("User ID é inválida !", del_in=5)
            return
        await kannax.block_user(user_id)
        blocked_msg = action_msg(user, "BLOCKED")
        await message.edit(blocked_msg, del_in=5, log=__name__)


@kannax.on_cmd(
    "unblock",
    about={
        "header": "Desbloqueia um usuário!",
        "usage": "{tr}unblock [ID] ou [Responda um Usuario]",
        "examples": "{tr}unblock @fnixdev",
    },
)
async def unblock_user(message: Message):
    """Desbloqueia um usuário!"""
    reply = message.reply_to_message
    if not (reply or message.input_str):
        await message.err("Responda a um usuário ou forneça ID para desbloqueá-lo!", del_in=5)
        return
    user_id = reply.from_user.id if reply else message.input_str
    if user_id in Config.OWNER_ID:
        await message.edit("Você está falando sério, mano? :/")
        await asyncio.sleep(2)
        await message.edit("Como é que eu vou me desbloquear? :|", del_in=5)
    else:
        try:
            user = await kannax.get_users(user_id)
        except BadRequest:
            await message.err("User ID é inválida !", del_in=5)
            return
        await kannax.unblock_user(user_id)
        unblocked_msg = action_msg(user, "UNBLOCKED")
        await message.edit(unblocked_msg, del_in=5, log=__name__)


def action_msg(user, action):
    return f"#{action}_USER\n>>  {mention_html(user.id, user.first_name)} foi <b>{action} em PM</b>."
