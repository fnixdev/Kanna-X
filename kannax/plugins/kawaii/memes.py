""" enjoy memes """

# All rights reserved.

import asyncio
import os
import random
import re
import requests
import wget
import datetime
import math
from cowpy import cow
from random imoort randint, choice

from kannax import Message, kannax


@kannax.on_cmd("yp$", about={"header": "Barra de progresso do ano"})
async def progresss(message):
    x = datetime.datetime.now()
    day = int(x.strftime("%j"))
    total_days = 365 if x.year % 4 != 0 else 366  # Haha Yes Finally
    percent = math.trunc(day / total_days * 100)
    num = round(percent / 5)

    progress = [
        "░░░░░░░░░░░░░░░░░░░░",
        "▓░░░░░░░░░░░░░░░░░░░",
        "▓▓░░░░░░░░░░░░░░░░░░",
        "▓▓▓░░░░░░░░░░░░░░░░░",
        "▓▓▓▓░░░░░░░░░░░░░░░░",
        "▓▓▓▓▓░░░░░░░░░░░░░░░",
        "▓▓▓▓▓▓░░░░░░░░░░░░░░",
        "▓▓▓▓▓▓▓░░░░░░░░░░░░░",
        "▓▓▓▓▓▓▓▓░░░░░░░░░░░░",
        "▓▓▓▓▓▓▓▓▓░░░░░░░░░░░",
        "▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
    ]

    message_out = f"<b>Progresso do ano</b>\n<code>{progress[num]} {percent}%</code>"
    await message.edit(message_out)



@kannax.on_cmd("fds", about={"header": "fodase?"})
async def fds_(message: Message):
    out_str = f"""
F
     O
　　 O
　　　O
　　　 o
ₒ ᵒ 。   o
ᵒ ₒ °ₒ  ᵒ
　 ˚
　°
　•
　 .
　　.   
           da-se?
    """
    await message.edit(out_str)


@kannax.on_cmd("(rt|Rt,)", about={"header": "rt message"}, trigger="", allow_via_bot=False)
async def rt_(message: Message):
    """rt mensagem"""
    retweet = message.reply_to_message
    try:
        rt_msg = retweet.text
        user_ = retweet.from_user.first_name
        user_me = await message.client.get_user_dict(message.from_user.id)
        usr_me = user_me["fname"]
        mensg = f"🔃 **{usr_me}** retweetou:\n\n👤 **{user_}**: __{rt_msg}__"
        await message.edit(mensg)
    except:
        pass

@kannax.on_cmd("f", about={"header": "f"})
async def f_(message: Message):
    paytext = message.reply_to_message
    pay = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        paytext * 8,
        paytext * 8,
        paytext * 2,
        paytext * 2,
        paytext * 2,
        paytext * 6,
        paytext * 6,
        paytext * 2,
        paytext * 2,
        paytext * 2,
        paytext * 2,
        paytext * 2,
    )
    await message.edit(pay)


@kannax.on_cmd("iam", about={"header": "i am gay?"})
async def iam_(message: Message):
    reply_ = message.reply_to_message
    if not reply_:
        iam = f"`🌈 I am {random.choice(range(0,100))}% gay!`"
        await message.edit(iam)
        return
    user_ = await kannax.get_users(reply_.from_user.id)
    msg_ = f"🌈 {user_.mention} `é {random.choice(range(0,100))}% gay!`"
    await message.edit(msg_)


@kannax.on_cmd("(Hmm)$", about={"header": "Hmmmmm"}, trigger="", allow_via_bot=False)
async def Hmm_(message: Message):
    """Hmm"""
    Hmm = "Hm "
    for _ in range(4):
        Hmm = Hmm[:-1] + "mm"
        await message.try_to_edit(Hmm)


@kannax.on_cmd("aa", about={"header": "aaaaaaaa"}, allow_via_bot=False)
async def aaa_(message: Message):
    """"""
    aa = "aa "
    for _ in range(4):
        aa = aa[:-1] + "aaaa"
        await message.try_to_edit(aa)


@kannax.on_cmd("(oof)$", about={"header": "ooooooof"}, trigger="", allow_via_bot=False)
async def oof_(message: Message):
    """oof"""
    Hmm = "ooo "
    for _ in range(15):
        Hmm = Hmm[:-1] + "ooof"
        await message.try_to_edit(Hmm)


@kannax.on_cmd("snake", about={"header": "sneeeeak"})
async def snake_(message: Message):
    out_str = f"""
░░░░▓
░░░▓▓
░░█▓▓█
░██▓▓██
░░██▓▓██
░░░██▓▓██
░░░░██▓▓██
░░░░░██▓▓██
░░░░██▓▓██
░░░██▓▓██
░░██▓▓██
░██▓▓██
░░██▓▓██
░░░██▓▓██
░░░░██▓▓██
░░░░░██▓▓██
░░░░██▓▓██
░░░██▓▓██
░░██▓▓██
░██▓▓██
░░██▓▓██
░░░██▓▓██
░░░░██▓▓██
░░░░░██▓▓██
░░░░██▓▓██
░░░██▓▓██
░░██▓▓██
░██▓▓██
░░██▓▓██
░░░██▓▓██
░░░░██▓▓██
░░░░░██▓▓██
░░░░██▓▓██
░░░██▓▓██
░░██▓▓██
░██▓▓██
░░██▓▓██
░░░██▓▓██
░░░░██▓▓██
░░░░░██▓▓██
░░░░██▓▓██
░░░██▓▓██
░░██▓▓██
░██▓▓██
░░██▓▓██
░░░██▓▓██
░░░░██▓▓██
░░░░░██▓▓██
░░░░██▓▓██
░░░██▓▓██
░░██▓▓██
░██▓▓██
░░██▓▓██
░░░██▓▓██
░░░░██▓▓██
░░░░░██▓▓██
░░░░██▓▓██
░░░██▓▓██
░░██▓▓██
░██▓▓██
░░██▓▓██
░░░██▓▓██
░░░░██▓▓██
░░░░░██▓▓██
░░░░██▓▓██
░░░██▓▓██
░░██▓▓██
░░██▓▓██
░░██▓▓██
░░██▓▓██
░ ██▓▓██
░░██▓▓██
░░░██▓▓███
░░░░██▓▓████
░░░░░██▓▓█████
░░░░░░██▓▓██████
░░░░░░███▓▓███████
░░░░░████▓▓████████
░░░░█████▓▓█████████
░░░█████░░░█████●███
░░████░░░░░░░███████
░░███░░░░░░░░░██████
░░██░░░░░░░░░░░████
░░░░░░░░░░░░░░░░██
    """
    await message.edit(out_str)


@kannax.on_cmd("lol", about={"header": "biglol"})
async def loll(message: Message):
    out_str = f"""
┏━┓┈┈╭━━━━╮┏━┓┈┈
┃╱┃┈┈┃╱╭╮╱┃┃╱┃┈┈
┃╱┗━┓┃╱┃┃╱┃┃╱┗━┓
┃╱╱╱┃┃╱╰╯╱┃┃╱╱╱┃
┗━━━┛╰━━━━╯┗━━━┛
    """
    await message.edit(out_str)


@kannax.on_cmd("(k|K)$", about={"header": "KKKKKKKKKKKKKKKKKKKK"}, trigger="", allow_via_bot=False)
async def kkk_(message: Message):
    """KK"""
    K = "K "
    for _ in range(4):
        K = K[:-1] + "KKKKKKKKKKK"
        await message.try_to_edit(K)


@kannax.on_cmd("(bd)$", about={"header": "bom diaaa"}, trigger="", allow_via_bot=False)
async def bd_(message: Message):
    """bd"""
    await message.edit("bom diaaa")


@kannax.on_cmd("(BD)$", about={"header": "Bom Diaaa"}, trigger="", allow_via_bot=False)
async def BD_(message: Message):
    """BD"""
    await message.edit("Bom Diaaa")


@kannax.on_cmd("(bn)$", about={"header": "boa noitee"}, trigger="", allow_via_bot=False)
async def bn_(message: Message):
    """bn"""
    await message.edit("boa noitee")


@kannax.on_cmd("(BN)$", about={"header": "Boa Noitee"}, trigger="", allow_via_bot=False)
async def BN_(message: Message):
    """BN"""
    await message.edit("Boa Noitee")


@kannax.on_cmd("(hmm)$", about={"header": "hmmmmm"}, trigger="", allow_via_bot=False)
async def hmm_(message: Message):
    """hmm"""
    hmm = "hm "
    for _ in range(4):
        hmm = hmm[:-1] + "mm"
        await message.try_to_edit(hmm)


async def check_and_send(message: Message, *args, **kwargs):
    replied = message.reply_to_message
    if replied:
        await asyncio.gather(message.delete(), replied.reply(*args, **kwargs))
    else:
        await message.edit(*args, **kwargs)


@kannax.on_cmd(r"(?:Kek|:/)$",
               about={'header': "Check yourself, hint: :/"}, name='Kek',
               trigger='', allow_via_bot=False)
async def kek_(message: Message):
    """kek"""
    kek = ["/", "\\"]
    for i in range(1, 9):
        await message.try_to_edit(":" + kek[i % 2])


@kannax.on_cmd(
    "clap",
    about={"header": "Praise people!",
           "usage": "{tr}clap [input | reply to msg]"},
)
async def clap_(message: Message):
    """clap"""
    input_str = message.input_or_reply_str
    if not input_str:
        await message.edit("`Hah, I don't clap pointlessly!`")
        return
    reply_text = "👏 "
    reply_text += input_str.replace(" ", " 👏 ")
    reply_text += " 👏"
    await message.edit(reply_text)


@kannax.on_cmd(
    "(\\w+)say (.+)",
    about={
        "header": "cow which says things",
        "usage": "{tr}[any cowacter]say [text]",
        "cowacters": f"`{'`,    `'.join(cow.COWACTERS)}`",
    },
    name="cowsay",
)
async def cowsay_(message: Message):
    """cowsay"""
    arg = message.matches[0].group(1).lower()
    text = message.matches[0].group(2)
    if arg == "cow":
        arg = "default"
    if arg not in cow.COWACTERS:
        await message.err("cowacter not found!")
        return
    cheese = cow.get_cow(arg)
    cheese = cheese()
    await message.edit(f"`{cheese.milk(text).replace('`', '´')}`")


@kannax.on_cmd(
    "coinflip",
    about={"header": "Flip a coin !!",
           "usage": "{tr}coinflip [heads | tails]"},
)
async def coin_(message: Message):
    """coin"""
    r = choice(["heads", "tails"])
    input_str = message.input_str
    if not input_str:
        return
    input_str = input_str.lower()
    if r == "heads":
        if input_str == "heads":
            await message.edit("The coin landed on: **Heads**.\nYou were correct.")
        elif input_str == "tails":
            await message.edit(
                "The coin landed on: **Heads**.\nYou weren't correct, try again ..."
            )
        else:
            await message.edit("The coin landed on: **Heads**.")
    elif r == "tails":
        if input_str == "tails":
            await message.edit("The coin landed on: **Tails**.\nYou were correct.")
        elif input_str == "heads":
            await message.edit(
                "The coin landed on: **Tails**.\nYou weren't correct, try again ..."
            )
        else:
            await message.edit("The coin landed on: **Tails**.")


@kannax.on_cmd(
    "(yes|no|maybe|decide)$",
    about={
        "header": "Make a quick decision",
        "examples": ["{tr}decide", "{tr}yes", "{tr}no", "{tr}maybe"],
    },
    name="decide",
)
async def decide_(message: Message):
    """decide"""
    decision = message.matches[0].group(1).lower()
    await message.edit("hmm...")
    if decision != "decide":
        r = requests.get(f"https://yesno.wtf/api?force={decision}").json()
    else:
        r = requests.get("https://yesno.wtf/api").json()
    path = wget.download(r["image"])
    chat_id = message.chat.id
    message_id = None
    if message.reply_to_message:
        message_id = message.reply_to_message.message_id
    await message.delete()
    await message.client.send_photo(
        chat_id=chat_id,
        photo=path,
        caption=str(r["answer"]).upper(),
        reply_to_message_id=message_id,
    )
    os.remove(path)


@kannax.on_cmd(
    "scam",
    about={
        "header": "Create fake chat actions, for fun.",
        "available actions": [
            "typing (default)",
            "playing",
            "upload_photo",
            "upload_video",
            "upload_audio",
            "upload_document",
            "upload_video_note",
            "record_video",
            "record_audio",
            "record_video_note",
            "find_location",
            "choose_contact",
        ],
        "usage": "{tr}scam\n{tr}scam [action]\n{tr}scam [time]\n{tr}scam [action] [time]",
    },
)
async def scam_(message: Message):
    """scam"""
    options = (
        "typing",
        "upload_photo",
        "record_video",
        "upload_video",
        "record_audio",
        "upload_audio",
        "upload_document",
        "find_location",
        "record_video_note",
        "upload_video_note",
        "choose_contact",
        "playing",
    )
    input_str = message.input_str
    args = input_str.split()
    if len(args) == 0:  # Let bot decide action and time
        scam_action = choice(options)
        scam_time = randint(30, 60)
    elif len(args) == 1:  # User decides time/action, bot decides the other.
        try:
            scam_action = str(args[0]).lower()
            scam_time = randint(30, 60)
        except ValueError:
            scam_action = choice(options)
            scam_time = int(args[0])
    elif len(args) == 2:  # User decides both action and time
        scam_action = str(args[0]).lower()
        scam_time = int(args[1])
    else:
        await message.edit("`Invalid Syntax !!`")
        return
    try:
        if scam_time > 0:
            chat_id = message.chat.id
            await message.delete()
            count = 0
            while count <= scam_time:
                await message.client.send_chat_action(chat_id, scam_action)
                await asyncio.sleep(5)
                count += 5
    except Exception:
        await message.delete()


@kannax.on_cmd("hack$", about={"header": "kensar hacking animation"})
async def hack_func(message: Message):
    user = await message.client.get_user_dict(message.from_user.id)
    heckerman = user["mention"]
    animation_chars = [
        "`Installing Files To Hacked Private Server...`",
        "`Target Selected.`",
        "`Installing... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Installing... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Installing... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`lnstallig... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Installing... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Installing... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Installing... 84%\n█████████████████████▒▒▒▒ `",
        "`Installing... 100%\n████████Installed██████████ `",
        "`Target files Uploading...\n\nDirecting To Remote  server to hack..`",
        "`root@kannax:~#` ",
        "`root@kannax:~# ls`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~#`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...\nroot@kannax:~# `",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...\nroot@kannax:~# touch setup.py`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...\nroot@kannax:~# touch setup.py\n\nsetup.py deployed ...`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...\nroot@kannax:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...\nroot@kannax:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@kannax:~# trap whoami`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...\nroot@kannax:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@kannax:~# trap whoami\n\nwhoami=user`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...\nroot@kannax:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@kannax:~# trap whoami\n\nwhoami=user\nboost_trap on force ...`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...\nroot@kannax:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@kannax:~# trap whoami\n\nwhoami=user\nboost_trap on force ...\nvictim detected in ghost ...`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...\nroot@kannax:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@kannax:~# trap whoami\n\nwhoami=user\nboost_trap on force ...\nvictim detected in ghost ...\n\nAll Done!`",
        "`root@kannax:~# ls\n\n  usr  ghost  codes  \n\nroot@kannax:~# # So Let's Hack it ...\nroot@kannax:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@kannax:~# trap whoami\n\nwhoami=user\nboost_trap on force ...\nvictim detected  in ghost ...\n\nAll Done!\nInstalling Token!\nToken=`DJ65gulO90P90nlkm65dRfc8I`",
        "`Hacking... 0% completed.\nTERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (1.3) kB`",
        "`Hacking... 4% completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Package`",
        "`hacking.....6% completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target account chat\n lding chat tg-bot bruteforce finished`",
        "`hacking.....8% completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target account chat\n lding chat tg-bot bruteforce finished\n creating pdf of chat`",
        "`hacking....15% completed\n Terminal:chat history from telegram exporting to private database.\n terminal 874379gvrfghhuu5tlotruhi5rbh installing`",
        "`hacking....24% completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target account chat\n lding chat tg-bot bruteforce finished\nerminal:chat history from telegram exporting to private database.\n terminal 874379gvrfghhuu5tlotruhi5rbh installed\n creting data into pdf`",
        "`hacking....32% completed\n looking for use history \n downloading-telegram -id prtggtgf . gfr (12.99 mb)\n collecting data starting imprute attack to user account\n chat history from telegram exporting to private database.\n terminal 874379gvrfghhuu5tlotruhi5rbh installed\n creted data into pdf\nDownload sucessful Bruteforce-Telegram-0.1.tar.gz (1.3)`",
        "`hacking....38% completed\n\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Package\n  Downloading Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB): finished with status 'done'\nCreated wheel for telegram: filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e`",
        "`hacking....52% completed\nexterting data from telegram private server\ndone with status 36748hdeg \n checking for more data in device`",
        "`hacking....60% completed\nmore data found im target device\npreparing to download data\n process started with status 7y75hsgdt365ege56es \n status changed to up`",
        "`hacking....73% completed\n downloading data from device\n process completed with status 884hfhjh\nDownloading-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target\n lding chat tg-bot bruteforce finished\n creating pdf of chat`",
        "`hacking...88% completed\nall data from telegram private server downloaded\nterminal download sucessfull--with status jh3233fdg66y yr4vv.irh\n data collected from tg-bot\nTERMINAL:\n Bruteforce-Telegram-0.1.tar.gz (1.3)downloaded`",
        "`100%\n█████████HACKED███████████ `\n\n\n  TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Package\n  Downloading Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB)\nBuilding wheel for Tg-Bruteforcing (setup.py): finished with status 'done'\nCreated wheel for telegram: filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e\n  Stored in directory: `",
        "`User Data Upload Completed: Target's User Data Stored `",
        "`at downloads/victim/telegram-authuser.data.sql`",
    ]
    hecked = (
        f"`Targeted Account Hacked\n\nPague 69$ a {heckerman}` "
        "`Para remover o hack.`"
    )
    max_ani = len(animation_chars)
    for i in range(max_ani):
        await asyncio.sleep(2)
        await message.edit(animation_chars[i % max_ani])
    await message.edit(hecked)


@kannax.on_cmd("kill$", about={"header": "Kill anybody With Full Power ;-)"})
async def kill_func(message):
    animation_chars = [
        "killing...",
        "Ｆｉｉｉｉｉｒｅ",
        "(　･ิω･ิ)︻デ═一-->",
        "------>_____________",
        "--------->___⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠_______",
        "-------------->_____",
        "------------------->",
        "------>;(^。^)ノ",
        "(￣ー￣) DED",
        "<b>Target killed successfully (´°̥̥̥̥̥̥̥̥ω°̥̥̥̥̥̥̥̥｀)</b>",
    ]
    for i in range(10):
        await asyncio.sleep(0.6)
        await message.edit(animation_chars[i % 10], parse_mode="html")
