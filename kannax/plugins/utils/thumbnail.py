""" custom thumbnail """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

import base64
import os
from datetime import datetime

import aiofiles

from kannax import Config, Message, get_collection, kannax
from kannax.utils import progress

SAVED_SETTINGS = get_collection("CONFIGS")
CHANNEL = kannax.getCLogger(__name__)


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({"_id": "CUSTOM_THUMB"})
    if data and not os.path.exists(Config.THUMB_PATH):
        with open(Config.THUMB_PATH, "wb") as thumb_file:
            thumb_file.write(base64.b64decode(data["data"]))


@kannax.on_cmd(
    "sthumb",
    about={"header": "Save thumbnail", "usage": "{tr}sthumb [reply to any photo]"},
)
async def save_thumb_nail(message: Message):
    """setup thumbnail"""
    await message.edit("processing ...")
    replied = message.reply_to_message
    if (
        replied
        and replied.media
        and (
            replied.photo
            or (replied.document and "image" in replied.document.mime_type)
        )
    ):
        start_t = datetime.now()
        if os.path.exists(Config.THUMB_PATH):
            os.remove(Config.THUMB_PATH)
        await message.client.download_media(
            message=replied,
            file_name=Config.THUMB_PATH,
            progress=progress,
            progress_args=(message, "trying to download"),
        )
        async with aiofiles.open(Config.THUMB_PATH, "rb") as thumb_file:
            media = base64.b64encode(await thumb_file.read())
        await SAVED_SETTINGS.update_one(
            {"_id": "CUSTOM_THUMB"}, {"$set": {"data": media}}, upsert=True
        )
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(f"thumbnail saved in {m_s} seconds.", del_in=3)
    else:
        await message.edit("Reply to a photo to save custom thumbnail", del_in=3)


@kannax.on_cmd("dthumb", about={"header": "Delete thumbnail"}, allow_channels=False)
async def clear_thumb_nail(message: Message):
    """delete thumbnail"""
    await message.edit("`processing ...`")
    if os.path.exists(Config.THUMB_PATH):
        os.remove(Config.THUMB_PATH)
        await SAVED_SETTINGS.find_one_and_delete({"_id": "CUSTOM_THUMB"})
        await message.edit("✅ Custom thumbnail deleted succesfully.", del_in=3)
    elif os.path.exists("resources/kannax.png"):
        os.remove("resources/kannax.png")
        await message.edit("✅ Default thumbnail deleted succesfully.", del_in=3)
    else:
        await message.delete()


@kannax.on_cmd("vthumb", about={"header": "View thumbnail"}, allow_channels=False)
async def get_thumb_nail(message: Message):
    """view current thumbnail"""
    await message.edit("processing ...")
    if os.path.exists(Config.THUMB_PATH):
        msg = await message.client.send_document(
            chat_id=message.chat.id,
            document=Config.THUMB_PATH,
            disable_notification=True,
            reply_to_message_id=message.message_id,
        )
        await CHANNEL.fwd_msg(msg)
        await message.delete()
    else:
        await message.err("Custom Thumbnail Not Found!")
