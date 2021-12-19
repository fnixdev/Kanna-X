
import base64
import requests
import os
from random import choice
from kannax import kannax, Message

api1 = base64.b64decode("QUl6YVN5QXlEQnNZM1dSdEI1WVBDNmFCX3c4SkF5NlpkWE5jNkZV").decode(
    "ascii"
)
api2 = base64.b64decode("QUl6YVN5QkYwenhMbFlsUE1wOXh3TVFxVktDUVJxOERnZHJMWHNn").decode(
    "ascii"
)
api3 = base64.b64decode("QUl6YVN5RGRPS253blB3VklRX2xiSDVzWUU0Rm9YakFLSVFWMERR").decode(
    "ascii"
)

@kannax.on_cmd("mod", about={"header": "search mods"})
async def mods_(message: Message):
    query = message.input_str
    r = choice([api1, api2, api3])
    page = 1
    start = (page - 1) * 3 + 1
    if " " in query:
        query.replace(" ").replace("%20")
    url = f"https://www.googleapis.com/customsearch/v1?key={r}&cx=25b3b50edb928435b&q={query}&start={start}"
    data = requests.get(url).json()
    search_items = data.get("items")
    for a in search_items:
        title = a.get("title")
        desc = a.get("snippet")
        link = a.get("link")
        text = f"**• Titulo** `{title}`\n\n"
        text += f"**• Desc:** `{desc}`"
        text += f"**• Link:** {link}"
    await message.edit(text)