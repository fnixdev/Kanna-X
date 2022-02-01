# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

"""coisas relacionadas a android"""

from bs4 import BeautifulSoup
from requests import get
from kannax import Message, kannax
import requests


DEVICE_LIST = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"


@kannax.on_cmd(
    "device",
    about={"header": "Encontre dispositivo pelo codename",
           "usage": "{tr}device [codename]"},
    allow_via_bot=True,
)
async def device_info(message: Message):
    if len(message.text.split()) == 1:
        await message.edit("`Quer que eu adivinhe? Por favor digite um codename`")
        return
    getlist = requests.get(DEVICE_LIST).json()
    target_device = message.text.split()[1].lower()
    if target_device in list(getlist):
        device = getlist.get(target_device)
        text = ""
        for x in device:
            text += f"Brand: `{x['brand']}`\nName: `{x['name']}`\nDevice: `{x['model']}`\nCodename: `{target_device}`"
            text += "\n\n"
        await message.edit(text)
    else:
        await message.edit(f"Device {target_device} não foi encontrado!")
        await sleep(5)
        await message.delete()


@kannax.on_cmd(
    "twrp",
    about={"header": "Encontre TWRP para seu dispositivo",
           "usage": "{tr}twrp <codename>"},
    allow_via_bot=True,
)
async def device_recovery(message: Message):
    """Get Latest TWRP"""
    message.reply_to_message
    args = message.filtered_input_str
    if args:
        device = args
    else:
        await message.err("```Insira o codename do dispositivo !!```", del_in=3)
        return
    await message.delete()
    url = get(f"https://dl.twrp.me/{device}/")
    if url.status_code == 404:
        reply = f"`Não foi encontrado TWRP para {device}!`\n"
        return await message.edit(reply, del_in=5)
    page = BeautifulSoup(url.content, "lxml")
    download = page.find("table").find("tr").find("a")
    dl_link = f"https://dl.twrp.me{download['href']}"
    dl_file = download.text
    size = page.find("span", {"class": "filesize"}).text
    date = page.find("em").text.strip()
    reply = (
        f"**TWRP mais recente para {device}:**\n"
        f"[{dl_file}]({dl_link}) - __{size}__\n"
        f"**Atualizado:** __{date}__"
    )
    await message.edit(reply)


@kannax.on_cmd("magisk$", about={"header": "Obtenha o magisk mais recente"})
async def magisk_(message: Message):
    """magisk mais recente"""
    magisk_repo = "https://raw.githubusercontent.com/fnixdev/magisk-files/"
    magisk_dict = {
        "⦁ 𝗦𝘁𝗮𝗯𝗹𝗲": magisk_repo + "master/stable.json",
        "⦁ 𝗕𝗲𝘁𝗮": magisk_repo + "master/beta.json",
        "⦁ 𝗖𝗮𝗻𝗮𝗿𝘆": magisk_repo + "master/canary.json",
    }
    releases = "<code><i>Versão mais recente do magisk:</i></code>\n\n"
    for name, release_url in magisk_dict.items():
        data = get(release_url).json()
        if "canary" in release_url:
            data["app"]["link"] = magisk_repo + "canary/" + data["app"]["link"]
            data["magisk"]["link"] = magisk_repo + \
                "canary/" + data["magisk"]["link"]
            data["uninstaller"]["link"] = (
                magisk_repo + "canary/" + data["uninstaller"]["link"]
            )

        releases += (
            f'{name}: [ZIP v{data["magisk"]["version"]}]({data["magisk"]["link"]}) | '
            f'[APK v{data["app"]["version"]}]({data["app"]["link"]}) | '
            f'[Uninstaller]({data["uninstaller"]["link"]})\n'
        )

    await message.edit(releases, disable_web_page_preview=True)
