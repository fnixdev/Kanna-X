# Plugin feito e disponibilizado por @yusukesy

from kannax import Config, kannax

import time

import asyncio

from bs4 import BeautifulSoup as bs
import requests

from sqlalchemy import create_engine, Column, Numeric, String, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


DATABASE_URL = "sqlite:///:memory:"

def start() -> scoped_session:
    engine = create_engine(DATABASE_URL)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))

try:
    BASE = declarative_base()
    SESSION = start()
except AttributeError as e:
    print("DATABASE_URL não foi configurada.")
    print(str(e))
    
class database(BASE):
    __tablename__ = "database"
    website = Column(String, primary_key=True)
    link = Column(String)
    
    def __init__(self, website, link):
        self.website = website
        self.link = link
        
database.__table__.create(checkfirst=True)

def get_link(website):
    try:
        return SESSION.query(database).get(website)
    finally:
        SESSION.close()
        
def add_link(website, link):
    checar = get_link(website)
    if not checar:
        adder = database(website, link)
        SESSION.add(adder)
        SESSION.commit()
    rem = SESSION.query(database).get(website)
    SESSION.delete(rem)
    SESSION.commit()
    adder = database(website, link)
    SESSION.add(adder)
    SESSION.commit()

async def check_link():
    html = requests.get("https://github.com/fnixdev/Kanna-X/commits/master").content
    soup = bs(html, "html.parser")
    try:
        link = "https://github.com" + str(soup.p.a.get("href"))
        website = "https://github.com/fnixdev/Kanna-X"
        if get_link(website) == None:
            add_link(website, "*") 
        if link != get_link(website).link:
            add_link(website, link)
            await kannax.bot.send_message(Config.LOG_CHANNEL_ID, f"**Nova atualização disponível**\n\nPara atualizar, use o comando `{Config.CMD_TRIGGER}update -pull`.")
    except:
        pass

async def main():
    while True:
        await check_link()
        await asyncio.sleep(2)
    
asyncio.get_event_loop().run_until_complete(main())