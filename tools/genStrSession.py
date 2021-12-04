# pylint: disable=invalid-name, missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

import os
import asyncio

from pyrogram import Client
from dotenv import load_dotenv

API_KEY = int(input("Enter API_ID: "))
API_HASH = input("Enter API_HASH: ")
with Client(':memory:', api_id=API_KEY, api_hash=API_HASH) as app:
	app.send_message(            
	  "me", f"#KannaX #HU_STRING_SESSION\n\n```{await kannax.export_session_string()}```")
	print("Pronto !, string de sessão foi enviada para mensagens salvas!")

