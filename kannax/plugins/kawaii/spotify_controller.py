
from kannax import kannax, Message
from kannax.utils import spotify


@kannax.on_cmd("np", about={"header": "now playing"})
async def np_(message: Message):
    current_track = await spotify.now_playing()

    if not current_track:
        await message.edit("I am not playing any music right now!")
        return

    if current_track == "API details not set":
        await message.edit("API details not set. Please read the README!")
        return

    track = current_track['item']
    song = track['name']
    link = track['external_urls']['spotify']

    await message.edit(f'🎶 Currently Playing: <a href="{link}">{song}</a>')


@kannax.on_cmd("spause", about={"header": "pause spotify"})
async def pause_(message: Message):
    pause = await spotify.pause()
    if pause:
        await message.edit("Spotify playback paused")
    else:
        await message.edit("Nothing is playing on Spotify")

    if pause == "API details not set":
        await message.edit("API details not set. Please read the README!")
        return


@kannax.on_cmd("splay", about={"header": "spotify play"})
async def play_(message: Message):
    play = await spotify.play()
    if play:
        await message.edit("Spotify playback started")
    else:
        await message.edit("Playing something already?")

    if play == "API details not set":
        await message.edit("API details not set. Please read the README!")
        return

