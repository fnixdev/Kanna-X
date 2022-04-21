# Plugin ytdl for KannaX by @fnixdev
#
# for kangs check #tags

from __future__ import unicode_literals

import os
import json

from yt_dlp import YoutubeDL
from youtubesearchpython import SearchVideos
from wget import download

from kannax import kannax, Config, Message
from ..bot.utube_inline import BASE_YT_URL, get_yt_video_id

LOGGER = kannax.getLogger(__name__)

# retunr regex link or get link with query
async def get_link(query):
    vid_id = get_yt_video_id(query)
    link = f"{BASE_YT_URL}{vid_id}"
    if vid_id is None:
        try:
            res_ = SearchVideos(query, offset=1, mode="json", max_results=1)
            link = json.loads(res_.result())["search_result"][0]["link"]
            id_ = link = json.loads(res_.result())["search_result"][0]["id"]
            return link, id_
        except Exception as e:
            LOGGER.exception(e)
            return e
    else:
        return link, vid_id

# yt-dl args - extract video info
async def extract_inf(link, opts_):
    with YoutubeDL(opts_) as ydl:
        infoo = ydl.extract_info(link, False)
        ydl.process_info(infoo)
        duration_ = infoo["duration"]
        title_ = infoo["title"]
        channel_ = infoo["channel"]
        views_ = infoo["view_count"]
        capt_ = f"<a href={link}><b>{title_}</b></a>\n❯ Duração: {duration_}\n❯ Views: {views_}\n❯ Canal: {channel_}"
        return capt_, title_, duration_


@kannax.on_cmd(
    "song",
    about={
        "header": "Music Downloader",
        "description": "Baixe músicas usando o yt_dlp",
        'options': {'-f': 'para baixar em formato flac'},
        'examples': ['{tr}song link',
                     '{tr}song nome da musica',
                     '{tr}song -f nome da musica']
        }
    )
async def song_(message: Message):
    chat_id = message.chat.id
    query = message.input_str
    if not query:
        return await message.edit("`Vou baixar o vento?!`", del_in=5)
    await message.edit("`Aguarde ...`")
    if query.startswith("-f"):
        format_ = "flac/best"
        fid = "flac"
    else:
        format_ = "bestaudio/best"
        fid = "mp3"
    aud_opts = {
        "outtmpl": os.path.join(Config.DOWN_PATH, "%(title)s.%(ext)s"),
        "logger": LOGGER,
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        'format': format_,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
                {
                     'key': 'FFmpegExtractAudio',
                     'preferredcodec': fid,
                     'preferredquality': '320',
                 },
            {"key": "EmbedThumbnail"},
            {"key": "FFmpegMetadata"},
        ],
        "quiet": True,
    }
    query_ = query.strip("-f")
    link, vid_id = await get_link(query_)
    await message.edit("`Processando o audio ...`")
    thumb_ = download(f"https://i.ytimg.com/vi/{vid_id}/maxresdefault.jpg", Config.DOWN_PATH)
    capt_, title_, duration_ = await extract_inf(link, aud_opts)
    capt_ += f"\n❯ Formato: {fid}"
    await message.delete()
    await message.client.send_audio(chat_id, audio=f"{Config.DOWN_PATH}{title_}.{fid}", caption=capt_, thumb=thumb_, duration=duration_)
    os.remove(f"{Config.DOWN_PATH}{title_}.{fid}")
    os.remove(f"{Config.DOWN_PATH}maxresdefault.jpg")


@kannax.on_cmd(
    "video",
    about={
        "header": "Video Downloader",
        "description": "Baixe videos usando o yt_dlp",
        'examples': ['{tr}video link',
                     '{tr}video nome do video',]
        }
    )
async def vid_(message: Message):
    chat_id = message.chat.id
    query = message.input_str
    if not query:
        return await message.edit("`Vou baixar o vento?!`", del_in=5)
    await message.edit("`Aguarde ...`")
    vid_opts = {
        "outtmpl": os.path.join(Config.DOWN_PATH, "%(title)s.%(ext)s"),
        'logger': LOGGER,
        'writethumbnail': False,
        'prefer_ffmpeg': True,
        'format': 'bestvideo+bestaudio/best',
        'postprocessors': [
                {
                    'key': 'FFmpegMetadata'
                }
            ],
        "quiet": True,
    }
    link, vid_id = await get_link(query)
    thumb_ = download(f"https://i.ytimg.com/vi/{vid_id}/maxresdefault.jpg", Config.DOWN_PATH)
    await message.edit("`Processando o video ...`")
    capt_, title_, duration_ = await extract_inf(link, vid_opts)
    await message.delete()
    await message.client.send_video(chat_id, video=f"{Config.DOWN_PATH}{title_}.webm", caption=capt_, thumb=thumb_, duration=duration_)
    os.remove(f"{Config.DOWN_PATH}{title_}.webm")
    os.remove(f"{Config.DOWN_PATH}maxresdefault.jpg")
