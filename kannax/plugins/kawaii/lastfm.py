# lastfm module by @fnix

import urllib.parse
import urllib.request
import rapidjson as json
import asyncio
import httpx

from kannax import kannax, Message, Config


BASE_LAST = "http://ws.audioscrobbler.com/2.0"
LAST_USER = Config.LASTFM_USERNAME
LAST_KEY = Config.LASTFM_API_KEY

timeout = httpx.Timeout(20)
http = httpx.AsyncClient(http2=True, timeout=timeout)

@kannax.on_cmd(
    "(lastfm|lt)",
    about={"header": "Mostra o que você esta ouvindo no momento"},
)
async def last_fm_pic_(message: Message):
    """now playing"""
    if not await check_lastfmvar(message):
        return
    resp = await http.get(
        f"{BASE_LAST}?method=user.getrecenttracks&limit=3&extended=1&user={LAST_USER}&api_key={LAST_KEY}&format=json"
    )
    if not resp.status_code == 200:
        await message.reply("__Algo deu errado__")
        return
    try:
        first_track = resp.json().get("recenttracks").get("track")[0]
    except IndexError:
        await message.edit("Você não scrobblou nenhuma música...")
        return
    image = first_track.get("image")[3].get("#text")
    artist = first_track.get("artist").get("name")
    artist_ = urllib.parse.quote(artist)
    song = first_track.get("name")
    song_ = urllib.parse.quote(song)
    loved = int(first_track.get("loved"))
    fetch = await http.get(
        f"{BASE_LAST}?method=track.getinfo&artist={artist_}&track={song_}&user={LAST_USER}&api_key={LAST_KEY}&format=json"
    )
    info = json.loads(fetch.content)
    last_user = info["track"]
    get_scrob = int(last_user["userplaycount"]) + 1
    rep = f"**{LAST_USER} esta ouvindo:**\n\n"
    if not loved:
        rep += f"<b>🎶 Musica:</b>  <i>{song}</i>\n<b>👥 Artista:</b>  <i>{artist}</i>"
    else:
        rep += f"<b>🎶 Musica:</b>  <i>{song}</i> ❤️(loved)\n<b>👥 Artista:</b>  <i>{artist}</i>"
    if get_scrob:
        rep += f"\n\n__📊 {get_scrob} scrobbles__"
    if image:
        rep += f"<a href='{image}'>\u200c</a>"
    await message.edit(rep)
    
    
async def check_lastfmvar(message: Message):
    if hasattr(Config, "LASTFM_API_KEY") and (
        Config.LASTFM_API_KEY and Config.LASTFM_USERNAME
    ):
        return True
    await message.edit(
        "**LastFm Config Vars não encontradas !\n Veja este [Guia](https://fnixdev.gitbook.io/kannax/variaveis-necessarias-para-kannax/vars_opcionais/lastfm) para mais informações.**"
    )
    return False