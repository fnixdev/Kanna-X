# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev


from pyrogram.errors.exceptions.bad_request_400 import (
    AboutTooLong,
    UsernameNotOccupied,
    VideoFileInvalid)

import asyncio
import base64
import os
from datetime import datetime
import textwrap
from shutil import copyfile
from asyncio import sleep


import aiofiles
from PIL import Image, ImageDraw, ImageFont

from kannax import Config, Message, get_collection, kannax
from kannax.utils import progress, is_dev

SAVED_SETTINGS = get_collection("CONFIGS")
UPDATE_PIC = False
BASE_PIC = "resources/base_profile_pic.jpg"
MDFY_PIC = "resources/mdfy_profile_pic.jpg"
LOG = kannax.getLogger(__name__)

PHOTO = Config.DOWN_PATH + "profile_pic.jpg"
USER_DATA = {}


async def _init() -> None:
    global UPDATE_PIC  # pylint: disable=global-statement
    data = await SAVED_SETTINGS.find_one({"_id": "UPDATE_PIC"})
    if data:
        UPDATE_PIC = data["on"]
        if not os.path.exists(BASE_PIC):
            with open(BASE_PIC, "wb") as media_file_:
                media_file_.write(base64.b64decode(data["media"]))


@kannax.on_cmd(
    "autopic",
    about={
        "header": "definir foto de perfil",
        "usage": "{tr}autopic\n{tr}autopic [image path]\nset timeout using {tr}sapicto",
    },
    allow_channels=False,
    allow_via_bot=False,
)
async def autopic(message: Message):
    global UPDATE_PIC  # pylint: disable=global-statement
    await message.edit("`processando...`")
    if UPDATE_PIC:
        if isinstance(UPDATE_PIC, asyncio.Task):
            UPDATE_PIC.cancel()
        UPDATE_PIC = False
        await SAVED_SETTINGS.update_one(
            {"_id": "UPDATE_PIC"}, {"$set": {"on": False}}, upsert=True
        )
        await asyncio.sleep(1)
        await message.edit("`definindo foto antiga...`")
        await kannax.set_profile_photo(photo=BASE_PIC)
        await message.edit(
            "a atualização automática da foto do perfil foi **interrompida**", del_in=5, log=__name__
        )
        return
    image_path = message.input_str
    store = False
    if os.path.exists(BASE_PIC) and not image_path:
        pass
    elif not image_path:
        profile_photo = await kannax.get_profile_photos("me", limit=1)
        if not profile_photo:
            await message.err("desculpe, não consegui encontrar nenhuma foto!")
            return
        await kannax.download_media(profile_photo[0], file_name=BASE_PIC)
        store = True
    else:
        if not os.path.exists(image_path):
            await message.err("caminho de entrada não encontrado!")
            return
        if os.path.exists(BASE_PIC):
            os.remove(BASE_PIC)
        copyfile(image_path, BASE_PIC)
        store = True
    data_dict = {"on": True}
    if store:
        async with aiofiles.open(BASE_PIC, "rb") as media_file:
            media = base64.b64encode(await media_file.read())
        data_dict["media"] = media
    await SAVED_SETTINGS.update_one(
        {"_id": "UPDATE_PIC"}, {"$set": data_dict}, upsert=True
    )
    await message.edit(
        "a atualização automática da foto do perfil foi **iniciada**", del_in=3, log=__name__
    )
    UPDATE_PIC = asyncio.get_event_loop().create_task(apic_worker())


@kannax.add_task
async def apic_worker():
    user_dict = await kannax.get_user_dict("me")
    user = "@" + \
        user_dict["uname"] if user_dict["uname"] else user_dict["flname"]
    count = 0
    while UPDATE_PIC:
        if not count % Config.AUTOPIC_TIMEOUT:
            img = Image.open(BASE_PIC)
            i_width, i_height = img.size
            s_font = ImageFont.truetype(
                "resources/font.ttf", int((35 / 640) * i_width))
            l_font = ImageFont.truetype(
                "resources/font.ttf", int((50 / 640) * i_width))
            draw = ImageDraw.Draw(img)
            current_h, pad = 10, 0
            for user in textwrap.wrap(user, width=20):
                u_width, u_height = draw.textsize(user, font=l_font)
                draw.text(
                    xy=((i_width - u_width) / 2,
                        int((current_h / 640) * i_width)),
                    text=user,
                    font=l_font,
                    fill=(255, 255, 255),
                )
                current_h += u_height + pad
            tim = datetime.datetime.now(
                tz=datetime.timezone(datetime.timedelta(minutes=30, hours=5))
            )
            date_time = (
                f"DATA: {tim.day}.{tim.month}.{tim.year}\n"
                f"TIME: {tim.hour}:{tim.minute}:{tim.second}\n"
                "UTC-3:00"
            )
            d_width, d_height = draw.textsize(date_time, font=s_font)
            draw.multiline_text(
                xy=(
                    (i_width - d_width) / 2,
                    i_height - d_height - int((20 / 640) * i_width),
                ),
                text=date_time,
                fill=(255, 255, 255),
                font=s_font,
                align="center",
            )
            img.convert("RGB").save(MDFY_PIC)
            await kannax.set_profile_photo(photo=MDFY_PIC)
            os.remove(MDFY_PIC)
            LOG.info("foto do perfil foi atualizada!")
        await asyncio.sleep(1)
        count += 1
    if count:
        LOG.info("a atualização da foto do perfil foi interrompida!")


@kannax.on_cmd("bio", about={
    'header': "Update bio, Maximum limit 70 characters",
    'flags': {
        '-delbio': "delete bio"},
    'usage': "{tr}bio [flag] \n"
             "{tr}bio [Bio]",
    'examples': [
        "{tr}bio -delbio",
        "{tr}bio  My name is krishna :-)"]}, allow_via_bot=False)
async def bio_(message: Message):
    """ Set or delete profile bio """
    if not message.input_str:
        await message.err("Need Text to Change Bio...")
        return
    if '-delbio' in message.flags:
        await kannax.update_profile(bio="")
        await message.edit("```Bio is Successfully Deleted ...```", del_in=3)
        return
    if message.input_str:
        try:
            await kannax.update_profile(bio=message.input_str)
        except AboutTooLong:
            await message.err("Bio is More then 70 characters...")
        else:
            await message.edit("```My Profile Bio is Successfully Updated ...```", del_in=3)


@kannax.on_cmd('setpic', about={
    'header': "Set profile picture",
    'usage': "{tr}setpic [reply to any photo]"}, allow_via_bot=False)
async def set_profile_picture(message: Message):
    """ Set Profile Picture """
    await message.edit("```processing ...```")

    replied = message.reply_to_message
    s_time = datetime.now()

    if (replied and replied.media and (
            replied.photo or (replied.document and "image" in replied.document.mime_type))):

        await kannax.download_media(message=replied,
                                    file_name=PHOTO,
                                    progress=progress,
                                    progress_args=(
                                        message, "trying to download and set profile picture"))

        await kannax.set_profile_photo(photo=PHOTO)

        if os.path.exists(PHOTO):
            os.remove(PHOTO)
        e_time = datetime.now()
        t_time = (e_time - s_time).seconds
        await message.edit(f"`Profile picture set in {t_time} seconds.`")

    elif (replied and replied.media and (
            replied.video or replied.animation)):
        VIDEO = Config.DOWN_PATH + "profile_vid.mp4"
        await kannax.download_media(message=replied,
                                    file_name=VIDEO,
                                    progress=progress,
                                    progress_args=(
                                        message, "trying to download and set profile picture"))

        try:
            await kannax.set_profile_photo(video=VIDEO)
        except VideoFileInvalid:
            await message.err("Video File is Invalid")
        else:
            e_time = datetime.now()
            t_time = (e_time - s_time).seconds

            await message.edit(f"`Profile picture set in {t_time} seconds.`")
    else:
        await message.err("Reply to any photo or video to set profile pic...")


@kannax.on_cmd('vpf', about={
    'header': "View Profile of any user",
    'flags': {
        '-fname': "Print only first name",
        '-lname': "Print only last name",
        '-flname': "Print full name",
        '-bio': "Print bio",
        '-uname': "Print username",
        '-pp': "Upload profile picture"},
    'usage': "{tr}vpf [flags]\n{tr}vpf [flags] [reply to any user]",
    'note': "<b> -> Use 'me' after flags to print own profile</b>\n"
            "<code>{tr}vpf [flags] me</code>"})
async def view_profile(message: Message):
    """ View Profile  """

    if not message.input_or_reply_str:
        await message.err("User id / Username not found...")
        return
    if message.reply_to_message:
        input_ = message.reply_to_message.from_user.id
    else:
        input_ = message.filtered_input_str
    if not input_:
        await message.err("User id / Username not found...")
        return
    if not message.flags:
        await message.err("Flags Required")
        return
    if "me" in message.filtered_input_str:
        user = await message.client.get_me()
        bio = (await message.client.get_chat("me")).bio
    else:
        try:
            user = await message.client.get_users(input_)
            bio = (await message.client.get_chat(input_)).bio
        except Exception:
            await message.err("invalid user_id!")
            return
    if '-fname' in message.flags:
        await message.edit("```checking, wait plox !...```", del_in=3)
        first_name = user.first_name
        await message.edit("<code>{}</code>".format(first_name), parse_mode='html')
    elif '-lname' in message.flags:
        if not user.last_name:
            await message.err("User not have last name...")
        else:
            await message.edit("```checking, wait plox !...```", del_in=3)
            last_name = user.last_name
            await message.edit("<code>{}</code>".format(last_name), parse_mode='html')
    elif '-flname' in message.flags:
        await message.edit("```checking, wait plox !...```", del_in=3)
        if not user.last_name:
            await message.edit("<code>{}</code>".format(user.first_name), parse_mode='html')
        else:
            full_name = user.first_name + " " + user.last_name
            await message.edit("<code>{}</code>".format(full_name), parse_mode='html')
    elif '-bio' in message.flags:
        if not bio:
            await message.err("User not have bio...")
        else:
            await message.edit("`checking, wait plox !...`", del_in=3)
            await message.edit("<code>{}</code>".format(bio), parse_mode='html')
    elif '-uname' in message.flags:
        if not user.username:
            await message.err("User not have username...")
        else:
            await message.edit("```checking, wait plox !...```", del_in=3)
            username = user.username
            await message.edit("<code>{}</code>".format(username), parse_mode='html')
    elif '-pp' in message.flags:
        if not user.photo:
            await message.err("profile photo not found!...")
        else:
            await message.edit("```checking pfp, wait plox !...```", del_in=3)
            await message.client.download_media(user.photo.big_file_id, file_name=PHOTO)
            await message.client.send_photo(message.chat.id, PHOTO)
            if os.path.exists(PHOTO):
                os.remove(PHOTO)


@kannax.on_cmd("delpfp", about={
    'header': "Delete Profile Pics",
    'description': "Delete profile pic in one blow"
                   " [NOTE: May Cause Flood Wait]",
    'usage': "{tr}delpfp [pfp count]"}, allow_via_bot=False)
async def del_pfp(message: Message):
    """ delete profile pics """
    if message.input_str:
        try:
            del_c = int(message.input_str)
        except ValueError as v_e:
            await message.err(v_e)
            return
        await message.edit(f"```Deleting first {del_c} Profile Photos ...```")
        start = datetime.now()
        ctr = 0
        async for photo in kannax.iter_profile_photos("me", limit=del_c):
            await kannax.delete_profile_photos(photo.file_id)
            ctr += 1
        end = datetime.now()
        difff = (end - start).seconds
        await message.edit(f"Deleted {ctr} Profile Pics in {difff} seconds!")
    else:
        await message.err("What am i supposed to delete nothing!...")
        await message.reply_sticker(sticker="CAADAQAD0wAD976IR_CYoqvCwXhyFgQ")


@kannax.on_cmd("clone", about={
    'header': "Clone first name, last name, bio and profile picture of any user",
    'flags': {
        '-fname': "Clone only first name",
        '-lname': "Clone only last name",
        '-bio': "Clone only bio",
        '-pp': "Clone only profile picture"},
    'usage': "{tr}clone [flag] [username | reply to any user]\n"
             "{tr}clone [username | reply to any user]",
    'examples': [
        "{tr}clone -fname username", "{tr}clone -lname username",
        "{tr}clone -pp username", "{tr}clone -bio username",
        "{tr}clone username"],
    'note': "<code>● Use revert after clone to get original profile</code>\n"
            "<code>● Don't use @ while giving username</code>"}, allow_via_bot=False)
async def clone_(message: Message):
    """ Clone first name, last name, bio and profile picture """
    if message.reply_to_message:
        input_ = message.reply_to_message.from_user.id
    else:
        input_ = message.filtered_input_str

    if not input_:
        await message.err("User id / Username not found!...")
        return
    if is_dev(input_):
        await message.reply("`FALHA NA M A T R I X\nNão posso clonar meu dev`")
        return
    await message.edit("`clonning...`")

    try:
        chat = await kannax.get_chat(input_)
        user = await kannax.get_users(input_)
    except UsernameNotOccupied:
        await message.err("Don't know that User!...")
        return
    me = await kannax.get_me()

    if '-fname' in message.flags:
        if 'first_name' in USER_DATA:
            await message.err("First Revert!...")
            return
        USER_DATA['first_name'] = me.first_name or ''
        await kannax.update_profile(first_name=user.first_name or '')
        await message.edit("```First Name is Successfully cloned ...```", del_in=3)
    elif '-lname' in message.flags:
        if 'last_name' in USER_DATA:
            await message.err("First Revert!...")
            return
        USER_DATA['last_name'] = me.last_name or ''
        await kannax.update_profile(last_name=user.last_name or '')
        await message.edit("```Last name is successfully cloned ...```", del_in=3)
    elif '-bio' in message.flags:
        if 'bio' in USER_DATA:
            await message.err("First Revert!...")
            return
        mychat = await kannax.get_chat(me.id)
        USER_DATA['bio'] = mychat.bio or ''
        await kannax.update_profile(bio=chat.description or '')
        await message.edit("```Bio is Successfully Cloned ...```", del_in=3)
    elif '-pp' in message.flags:
        if os.path.exists(PHOTO):
            await message.err("First Revert!...")
            return
        if not user.photo:
            await message.err("User not have any profile pic...")
            return
        await kannax.download_media(user.photo.big_file_id, file_name=PHOTO)
        await kannax.set_profile_photo(photo=PHOTO)
        await message.edit("```Profile photo is Successfully Cloned ...```", del_in=3)
    else:
        if USER_DATA or os.path.exists(PHOTO):
            await message.err("First Revert!...")
            return
        mychat = await kannax.get_chat(me.id)
        USER_DATA.update({
            'first_name': me.first_name or '',
            'last_name': me.last_name or '',
            'bio': mychat.description or ''})
        await kannax.update_profile(
            first_name=user.first_name or '',
            last_name=user.last_name or '',
            bio=chat.bio or '')
        if not user.photo:
            await message.edit(
                "`User not have profile photo, Cloned Name and bio...`", del_in=5)
            return
        await kannax.download_media(user.photo.big_file_id, file_name=PHOTO)
        await kannax.set_profile_photo(photo=PHOTO)
        await message.edit("```Profile is Successfully Cloned ...```", del_in=3)


@kannax.on_cmd("revert", about={
    'header': "Returns original profile",
    'usage': "{tr}revert"}, allow_via_bot=False)
async def revert_(message: Message):
    """ Returns Original Profile """
    if not (USER_DATA or os.path.exists(PHOTO)):
        await message.err("Already Reverted!...")
        return
    if USER_DATA:
        await kannax.update_profile(**USER_DATA)
        USER_DATA.clear()
    if os.path.exists(PHOTO):
        me = await kannax.get_me()
        photo = (await kannax.get_profile_photos(me.id, limit=1))[0]
        await kannax.delete_profile_photos(photo.file_id)
        os.remove(PHOTO)
    await message.edit("```Profile is Successfully Reverted...```", del_in=3)
