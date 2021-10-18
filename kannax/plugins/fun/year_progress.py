# by @deleteduser420
import datetime
import math

from kannax import kannax


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
