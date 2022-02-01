# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

from kannax import Message, kannax


@kannax.on_cmd("del", about={"header": "delete replied message"})
async def del_msg(message: Message):
    msg_ids = [message.message_id]
    if message.reply_to_message:
        msg_ids.append(message.reply_to_message.message_id)
    await message.client.delete_messages(message.chat.id, msg_ids)
