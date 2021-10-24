"""Last FM"""
# Copyright (C) 2020 BY KannaX
# All rights reserved.
#
# Authors: 1. https://github.com/lostb053 [TG: @Lostb053]
#          2. https://github.com/code-rgb [TG: @DeletedUser420]
#
# API: https://www.last.fm/api

import aiohttp
from kannax import Config, Message, kannax
from kannax.utils import get_response, rand_array

API = "http://ws.audioscrobbler.com/2.0"

# In Case Song Does't have any Album Art.
PIC_URL = [
    "https://telegra.ph/file/537e854be068680f1c05f.gif",
    "https://telegra.ph/file/e7b9dd5fe10f5e435a5b4.gif",
    "https://telegra.ph/file/d99d3afb149c922e57f58.gif",
    "https://telegra.ph/file/645a84a1430c6f6f0e679.gif",
    "https://telegra.ph/file/0f649b59da301c9c3d7ae.gif",
    "https://telegra.ph/file/5a00d9e2aeb2e45d85113.gif",
    "https://telegra.ph/file/871528bb25aacde193827.gif",
    "https://telegra.ph/file/4c50cdd484cc3b96a34ba.gif",
    "https://telegra.ph/file/8b70856135c3bf0250f88.gif",
    "https://telegra.ph/file/32b1e620f4eede44c74a0.gif",
    "https://telegra.ph/file/5d33b0371712a12160894.gif",
    "https://telegra.ph/file/a9b53a1940493e586cba5.gif",
]


@kannax.on_cmd(
    "lastfm",
    about={"header": "Mostra o que você esta ouvindo no momento"},
)
async def last_fm_pic_(message: Message):
    """now playing"""
    if not await check_lastfmvar(message):
        return
    params = {
        "method": "user.getrecenttracks",
        "limit": 1,
        "extended": 1,
        "user": Config.LASTFM_USERNAME,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.err("API LastFm inativa", del_in=5)
    if "error" in view_data:
        return await message.err(view_data["error"], del_in=5)
    recent_song = view_data["recenttracks"]["track"]
    if len(recent_song) == 0:
        return await message.err("Nenhuma trilha recente encontrada", del_in=5)
    rep = f"<i><b>{Config.LASTFM_USERNAME} atualmente está ouvindo:</b></i>\n"
    song_ = recent_song[0]
    song_name = song_["name"]
    artist_name = song_["artist"]["name"]
    rep += f"\n<b>🎶 Musica:</b>  <i>{song_name}</i>\n<b>👥 Artista:</b>  <i>{artist_name}</i>"
    if song_["loved"] != "0":
        rep += " (♥️ loved)"
    # Trying to Fetch Album of the track
    params_ = {
        "method": "track.getInfo",
        "track": song_name,
        "artist": artist_name,
        "user": Config.LASTFM_USERNAME, 
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data_ = await get_response.json(link=API, params=params_)
    except ValueError:
        return await message.err("API LastFm inativa", del_in=5)
    get_track = view_data_["track"]
    get_scrob = int(get_track["userplaycount"]) + 1
    scrobbler_ = f"\n<b>🎶 {get_scrob} Scrobbles</b>"
    img = get_track["album"]["image"][3].get("#text")
    get_tags = "\n"
    # tags of the given track
    for tags in get_track["toptags"]["tag"]:
        get_tags += f"<a href={tags['url']}>#{tags['name']}</a>  "
    await message.edit(f"<a href={img}>\u200c</a>" + rep + get_tags + scrobbler_, parse_mode="html")


@kannax.on_cmd(
    "lastuser",
    about={
        "header": "Obter informações do usuário Lastfm",
        "usage": "{tr}lastuser [lastfm username] (opcional)",
    },
)
async def last_fm_user_info_(message: Message):
    """user info"""
    if not await check_lastfmvar(message):
        return
    lfmuser = message.input_str or Config.LASTFM_USERNAME
    await message.edit(f"<code>Obtendo informações do usuario : {lfmuser}</code> ...")
    params = {
        "method": "user.getInfo",
        "user": lfmuser,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.err("API LastFm inativa", del_in=5)
    if "error" in view_data:
        return await message.err(view_data["error"], del_in=5)
    lastuser = view_data["user"]
    if lastuser["gender"] == "m":
        gender = "🙎‍♂️ "
    elif lastuser["gender"] == "f":
        gender = "🙍‍♀️ "
    else:
        gender = "👤 "
    lastimg = lastuser["image"].pop() if len(lastuser["image"]) != 0 else None
    age = lastuser["age"]
    playlist = lastuser["playlists"]
    subscriber = lastuser["subscriber"]
    result = ""
    if lastimg:
        result += f"<a href={lastimg['#text']}>\u200c</a>"
    result += f"<b>Informações do usuário LastFM para <a href={lastuser['url']}>{lfmuser}</a></b>:\n"
    result += f" {gender}<b>Nome:</b> {lastuser['realname']}\n"
    if age != "0":
        result += f" 🎂 <b>Idade:</b> {age}\n"
    result += f" 🎵 <b>Total Scrobbles:</b> {lastuser['playcount']}\n"
    result += f" 🌍 <b>País:</b> {lastuser['country']}\n"
    if playlist != "0":
        result += f" ▶️ <b>Playlists:</b> {playlist}\n"
    if subscriber != "0":
        result += f" ⭐️ <b>Subscriber:</b> {subscriber}"
    await message.edit(result, parse_mode="html")


@kannax.on_cmd(
    "lastlove",
    about={
        "header": "Obter faixas favoritas do Lastfm",
        "usage": "{tr}lastlove [lastfm username] (opcional)",
    },
)
async def last_fm_loved_tracks_(message: Message):
    """liked songs"""
    if not await check_lastfmvar(message):
        return
    user_ = message.input_str or Config.LASTFM_USERNAME
    await message.edit(f"♥️<code> Buscando faixas favoritas de {user_} ...</code>")
    params = {
        "method": "user.getlovedtracks",
        "limit": 30,
        "page": 1,
        "user": user_,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.err("API LastFm inativa", del_in=5)
    tracks = view_data["lovedtracks"]["track"]
    if "error" in view_data:
        return await message.err(view_data["error"], del_in=5)
    if len(tracks) == 0:
        return await message.edit("Você ainda não tem faixas favoritas.")
    rep = f"♥️ <b>Faixas favoritas de <a href=https://www.last.fm/user/{user_}>{user_}'s</a></b>"
    for count, song_ in enumerate(tracks, start=1):
        song_name = song_["name"]
        artist_name = song_["artist"]["name"]
        rep += f"\n{count:02d}. 🎧  <b><a href={song_['url']}>{song_name}</a></b> - <a href={song_['artist']['url']}>{artist_name}</a>"
    await message.edit(rep, disable_web_page_preview=True, parse_mode="html")


@kannax.on_cmd(
    "lastplayed",
    about={
        "header": "Obtenha músicas LastFm tocadas recentemente",
        "usage": "{tr}lastplayed [lastFM username] (opcional)",
    },
)
async def last_fm_played_(message: Message):
    """recently played songs"""
    await message.edit(
        "<code> 🎵 Buscando músicas reproduzidas recentemente de last.fm ...</code>"
    )
    if not await check_lastfmvar(message):
        return
    user_ = message.input_str or Config.LASTFM_USERNAME
    params = {
        "method": "user.getrecenttracks",
        "limit": 30,
        "extended": 1,
        "user": user_,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.err("API LastFm inativa", del_in=5)
    if "error" in view_data:
        return await message.err(view_data["error"], del_in=5)
    recent_song = view_data["recenttracks"]["track"]
    if len(recent_song) == 0:
        return await message.err("Nenhuma trilha recente encontrada", del_in=5)
    rep = f"<b><a href=https://www.last.fm/user/{user_}>{user_}'s</a></b> musicas tocadas recentemente:"
    for count, song_ in enumerate(recent_song, start=1):
        song_name = song_["name"]
        artist_name = song_["artist"]["name"]
        rep += f"\n{count:02d}. 🎧  <b><a href={song_['url']}>{song_name}</a></b> - <a href={song_['artist']['url']}>{artist_name}</a>"
        if song_["loved"] != "0":
            rep += " ♥️"
    await message.edit(rep, disable_web_page_preview=True, parse_mode="html")


async def check_lastfmvar(message: Message):
    if hasattr(Config, "LASTFM_API_KEY") and (
        Config.LASTFM_API_KEY and Config.LASTFM_USERNAME
    ):
        return True
    await message.edit(
        "**LastFm Config Vars não encontradas !\n Veja este [Guia](https://fnixdev.gitbook.io/kannax/variaveis-necessarias-para-kannax/vars_opcionais/lastfm) para mais informações.**"
    )
    return False

# The code i am using at the moment, this might work as it is, feel free to edit as per bot's use

du = "https://last.fm/user/"


async def resp(params: dict):
    async with aiohttp.ClientSession() as session, \
            session.get("http://ws.audioscrobbler.com/2.0", params=params) as res:
        return res.status, await res.json()


async def recs(query, typ, lim):
    params = {"method": f"user.get{typ}", "user": query, "limit": lim,
              "api_key": Config.LASTFM_API_KEY, "format": "json"}
    return await resp(params)

USERNAME = Config.LASTFM_USERNAME

@kannax.on_cmd(
    "compat",
    about={
        "header": "Compat",
        "description": "verifique o nível de compatibilidade de música com outros usuários de lastfm",
        "usage": "{tr}compat username ou {tr}compat username1|username2",
    },
)
async def lastfm_compat_(message: Message):
    """Mostra compatibilidade musical"""
    await message.edit(f"Processando...")
    msg = message.input_str
    if not msg:
        return await message.edit("Pls verifique `{tr}help compat`")
    diff = "|" in msg
    us1, us2 = msg.split("|") if diff else USERNAME, msg
    ta = "topartists"
    ta1 = (await recs(us1, ta, 500))[1][ta]["artist"]
    ta2 = (await recs(us2, ta, 500))[1][ta]["artist"]
    ad1, ad2 = [n["name"] for n in ta1], [n["name"] for n in ta2]
    display = f"****[{us1}]({du}{us1})**** e **[{us2}]({du}{us2})**"
    comart = [value for value in ad2 if value in ad1]
    disart = ", ".join({comart[r] for r in range(min(len(comart), 5))})
    compat = min((len(comart) * 100 / 40), 100)
    rep = f"{display} ambos ouvem: \n__{disart}__...\n\nCompatibilidade músical é de **{compat}%**"
    await message.edit(rep, disable_web_page_preview=True)