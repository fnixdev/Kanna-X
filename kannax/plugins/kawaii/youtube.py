# Plugin by https://github.com/RioProjectX/Rio-Music
# Ported for KannaX by @fnixdev

from __future__ import unicode_literals
import asyncio
import math
import os
import time
import aiofiles
import aiohttp
import requests
import yt_dlp
import wget
from random import randint
from urllib.parse import urlparse
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos

from kannax import kannax, Message
from kannax.utils import time_formatter, humanbytes

LOGGER = kannax.getLogger(__name__)
DURATION_LIMIT = int("60")

@kannax.on_cmd(
    "song",
    about={
        "header": "Music Download",
        "description": "Baixe musicas usando ytdl",
        "uso": "{tr}song [nome / reply msg / link]",
    },
)
async def song_(message: Message):
    query = message.input_or_reply_str
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    await message.edit("`Processando...`")
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://www.youtube.com{results[0]['url_suffix']}"
        # print(results)
        title = results[0]["title"]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        results[0]["url_suffix"]
        results[0]["views"]
    except Exception as e:
        await message.edit("❌ `Som não encontrado`\n\n`Tente inserir um título de música mais claro`")
        print(str(e))
        return
    await message.edit("📥 `Baixando`")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f"""
** Titulo :** __[{title}]({link})__
** Duração :** __{duration}__
** Views :** __{results[0]['views']}__
"""
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        await message.reply_audio(
            audio_file,
            caption=rep,
            thumb=thumb_name,
            parse_mode="md",
            title=title,
            duration=dur,
        )
        await message.delete()
    except Exception as e:
        await message.edit("❌ `Ocorreu algum erro, verifique o console.`")
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

#Def principais
async def progress(current, total, message, start, type_of_ps, file_name=None):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        if elapsed_time == 0:
            return
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "{0}{1} {2}%\n".format(
            "".join("🔴" for i in range(math.floor(percentage / 10))),
            "".join("🔘" for i in range(10 - math.floor(percentage / 10))),
            round(percentage, 2),
        )

        tmp = progress_str + "{0} of {1}\nETA: {2}".format(
            humanbytes(current), humanbytes(
                total), time_formatter(estimated_total_time)
        )
        if file_name:
            try:
                await message.edit(
                    "{}\n**File Name:** `{}`\n{}".format(
                        type_of_ps, file_name, tmp)
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass
        else:
            try:
                await message.edit("{}\n{}".format(type_of_ps, tmp))
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass


def get_readable_time(seconds: int) -> int:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["d", "m", "j", "hari"]
    while count < 4:
        count += 1
        remainder, result = divmod(
            seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time


ydl_opts = {
    "format": "bestaudio/best",
    "writethumbnail": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}


def get_file_extension_from_url(url):
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


# Funtion To Download Song
async def download_song(url):
    song_name = f"{randint(6969, 6999)}.mp3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(song_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
    return song_name


is_downloading = False


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


@kannax.on_cmd(
    "video",
    about={
        "header": "Video Download",
        "description": "Baixe videos usando ytdl",
        "uso": "{tr}video [nome / reply msg / link]",
    },
)
async def video_(message: Message):
    global is_downloading
    await message.edit("`Processando...`")
    if is_downloading:
        await message.reply_text(
            "`Outro download em andamento, tente novamente mais tarde`"
        )
        return
    s_video = message.input_or_reply_str
    if not s_video:
        await message.edit("`Syntax error`")
        return
    search = SearchVideos(f"{s_video}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    thums = mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        is_downloading = True
        with yt_dlp.YoutubeDL(opts) as ytdl:
            infoo = ytdl.extract_info(url, False)
            duration = round(infoo["duration"] / 60)

            if duration > DURATION_LIMIT:
                await message.edit(
                    f"`Vídeos com mais de {DURATION_LIMIT} minutos não são permitidos, os vídeos que você deseja baixar têm {duration} minutes**"
                )
                is_downloading = False
                return
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception:
        is_downloading = False
        return

    c_time = time.time()
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"**Título ➠** [{thum}]({mo}) \n**Canal ➠ ** {thums}"
    await message.client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        progress=progress,
        progress_args=(
            message,
            c_time,
            f"`Uploading {s_video}`",
            file_stark,
        ),
    )
    await message.delete()
    is_downloading = False
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)


