from kannax import Message, kannax


@kannax.on_cmd(
    "teste",
    about={
        "header": "Twitter screenshot",
        "description": "Obtenha screenshot de um link twitter",
        "usage": "{tr}tss [link]",
    },
)
async def teste_(message: Message):
    """apenas teste"""
    await message.edit("`Apenas um teste...`")