import html

from kannax import Message, kannax
from kannax.utils import mention_html


@kannax.on_cmd(
    "admins",
    about={
        "header": "Ver ou mencionar administradores no chat",
        "flags": {
            "-m": "mencionar todos os administradores",
            "-mc": "apenas mencione o criador",
            "-id": "mostrar ids",
        },
        "usage": "{tr}admins [any flag] [chatid]",
    },
    allow_channels=False,
)
async def mentionadmins(message: Message):
    owner_ = ""
    admins_ = ""
    bots_ = ""
    chat_id = message.filtered_input_str
    flags = message.flags
    men_admins = "-m" in flags
    men_creator = "-mc" in flags
    show_id = "-id" in flags
    if not chat_id:
        chat_id = message.chat.id
    mentions = "<b>Admins em {}</b>\n".format(
        (await message.client.get_chat(chat_id)).title
    )
    try:
        async for x in message.client.iter_chat_members(
            chat_id=chat_id, filter="administrators"
        ):
            status = x.status
            u_id = x.user.id
            username = x.user.username or None
            is_bot = x.user.is_bot
            full_name = (await message.client.get_user_dict(u_id))["flname"]
            if status == "creator":
                if men_admins or men_creator:
                    owner_ += f"\n 👑 {mention_html(u_id, full_name)}"
                elif username:
                    owner_ += "\n 👑 [{}](https://t.me/{})".format(
                        html.escape(full_name), username
                    )
                else:
                    owner_ += "\n 👑 [{}](tg://openmessage?user_id={})".format(
                        html.escape(full_name), u_id
                    )
                if show_id:
                    owner_ += f"  `{u_id}`"
            elif status == "administrator":
                if is_bot:
                    bots_ += f"\n 🤖 {mention_html(u_id, full_name)}"
                    if show_id:
                        bots_ += f"  `{u_id}`"
                else:
                    if men_admins:
                        admins_ += f"\n • {mention_html(u_id, full_name)}"
                    elif username:
                        admins_ += "\n • [{}](https://t.me/{})".format(
                            html.escape(full_name), username
                        )
                    else:
                        admins_ += "\n • [{}](tg://openmessage?user_id={})".format(
                            html.escape(full_name), u_id
                        )
                    if show_id:
                        admins_ += f"  `{u_id}`"

        mentions += f"{owner_}\n{admins_}{bots_}"
    except Exception as e:
        mentions += " " + str(e) + "\n"
    await message.edit(mentions, disable_web_page_preview=True)
