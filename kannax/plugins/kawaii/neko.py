import httpx
import requests
from kannax import Message, kannax
import re


@kannax.on_cmd(
    "neko",
    about={
        "header": "Obtenha nekos de nekos.life",
        "usage": "{tr}neko",
    },
)
async def random_neko(message: Message):
    try:
        r = requests.get("https://nekos.life/api/neko").json()
        neko = r["neko"]
        await message.delete()
        await message.reply_photo(neko)
    except Exception as e:
        await message.err(e)

@kannax.on_cmd(
    "cat",
    about={
        "header": "Obtenha gatinhos",
        "usage": "{tr}cat",
    },
)
async def random_cat(message: Message):
    async with httpx.AsyncClient() as client:
        reply = message.reply_to_message
        reply_id = reply.message_id if reply else None
        r = await client.get("https://api.thecatapi.com/v1/images/search")
    if not r.status_code == 200:
        return await message.edit(f"<b>Error!</b> <code>{r.status_code}</code>")
    cat = r.json
    await message.delete()
    await message.client.send_photo(
        chat_id=message.chat.id, photo=(cat()[0]["url"]), reply_to_message_id=reply_id)


@kannax.on_cmd(
    "dog",
    about={
        "header": "Obtenha doguinhos",
        "usage": "{tr}dog",
    },
)
async def random_dog(message: Message):
    async with httpx.AsyncClient() as client:
        reply = message.reply_to_message
        reply_id = reply.message_id if reply else None
        r = await client.get("https://api.thedogapi.com/v1/images/search")
    if not r.status_code == 200:
        return await message.edit(f"<b>Error!</b> <code>{r.status_code}</code>")
    dog = r.json
    await message.delete()
    await message.client.send_photo(
        chat_id=message.chat.id, photo=(dog()[0]["url"]), reply_to_message_id=reply_id)
