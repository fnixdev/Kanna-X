# Plugin ytdl for KannaX by @fnixdev
#
# for kangs check #tags

from __future__ import unicode_literals

import os
import glob
import json

from pathlib import Path
from yt_dlp import YoutubeDL
from youtubesearchpython import SearchVideos
from wget import download

from kannax import kannax, Config, Message
from ..bot.utube_inline import BASE_YT_URL, get_yt_video_id
from ..misc.utube import _mp3Dl
from ..misc.upload import upload


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
        filename_ = ydl.download(link)
        ydl.process_info(infoo)
        duration_ = infoo["duration"]
        title_ = infoo["title"].replace("/", "_")
        channel_ = infoo["channel"]
        views_ = infoo["view_count"]
        capt_ = f"<a href={link}><b>{title_}</b></a>\n❯ Duração: {duration_}\n❯ Views: {views_}\n❯ Canal: {channel_}"
        return capt_, filename_, duration_,


@kannax.on_cmd(
    "som",
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
    link, vid_id = await get_link(query)
    somg = _mp3Dl(link)
    if somg == 0:
        _fpath = ''
        for _path in glob.glob(os.path.join(Config.DOWN_PATH, '*')):
            if not _path.lower().endswith((".jpg", ".png", ".webp")):
                _fpath = _path
        if not _fpath:
            await message.err("nothing found !")
            return
        await message.reply_audio(audio=Path(_fpath))
    else:
        await message.edit(str(somg))


def _mp3Dl(url):
    _opts = {'outtmpl': os.path.join(Config.DOWN_PATH, '%(title)s.%(ext)s'),
             'logger': LOGGER,
             'writethumbnail': True,
             'prefer_ffmpeg': True,
             'format': 'bestaudio/best',
             'postprocessors': [
                 {
                     'key': 'FFmpegExtractAudio',
                     'preferredcodec': 'mp3',
                     'preferredquality': '320',
                 },
                 # {'key': 'EmbedThumbnail'},  ERROR: Conversion failed!
                 {'key': 'FFmpegMetadata'}]}
    try:
        x = YoutubeDL(_opts)
        dloader = x.download(url)
    except Exception as y_e:  # pylint: disable=broad-except
        LOGGER.exception(y_e)
        return y_e
    else:
        return dloader

"""
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
    capt_, filename_, duration_ = await extract_inf(link, aud_opts)
    capt_ += f"\n❯ Formato: {fid}"
    await message.delete()
    aud_file = filename_.replace("webm", fid)
    await message.client.send_audio(chat_id, audio=aud_file, caption=capt_, thumb=thumb_, duration=duration_)
    os.remove(aud_file)
    os.remove(f"{Config.DOWN_PATH}maxresdefault.jpg")
"""

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
    capt_, filename_, duration_ = await extract_inf(link, vid_opts)
    await message.delete()
    await message.client.send_video(chat_id, video=Path(filename_), caption=capt_, thumb=thumb_, duration=duration_)
    os.remove(filename_)
    os.remove(f"{Config.DOWN_PATH}maxresdefault.jpg")
