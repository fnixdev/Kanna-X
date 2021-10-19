#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

_checkBashReq() {
    log "Verificando Comandos Bash ..."
    command -v jq &> /dev/null || quit "Comando necessário :jq : não foi encontrado! !"
}

_checkPythonVersion() {
    log "Verificando a versão do Python..."
    getPythonVersion
    ( test -z $pVer || test $(sed 's/\.//g' <<< $pVer) -lt 3${minPVer}0 ) \
        && quit "Você DEVE ter uma versão python de pelo menos 3.$minPVer.0 !"
    log "\tPYTHON encontrado- v$pVer ..."
}

_checkConfigFile() {
    log "Verificando o arquivo de configuração ..."
    configPath="config.env"
    if test -f $configPath; then
        log "\tArquivo de configuração encontrado : $configPath, Exportando ..."
        set -a
        . $configPath
        set +a
        test ${_____REMOVE_____THIS_____LINE_____:-fasle} = true \
            && quit "Remova a linha mencionada na primeira hashtag do arquivo config.env"
    fi
}

_ativarlog() {
    log "Tentando ativar log de att..."
    local logErr=$(runPythonCode '
from kannax import Config
import telebot

import time

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

def check_link():
    html = requests.get("https://github.com/fnixdev/Kanna-X/commits/master").content
    soup = bs(html, "html.parser")
    try:
        link = "https://github.com" + str(soup.p.a.get("href"))
        website = "https://github.com/fnixdev/Kanna-X"
        if get_link(website) == None:
            add_link(website, "*") 
        if link != get_link(website).link:
            add_link(website, link)
            telebot.TeleBot(2051885612:AAHP65w_XYh-aFPv_K8NIpZ8WgKY6Em19qc).send_message(1157759484, f"<b>Nova atualização disponível!</b>\n\nPara atualizar, use o comando `.update -pull`.")
    except:
        pass

while True:
    print("oi")
    check_link()
    time.sleep(2)
    
telebot.TeleBot(2051885612:AAHP65w_XYh-aFPv_K8NIpZ8WgKY6Em19qc).infinity_polling()')
    [[ $logErr ]] && quit "E EU SLÁ $logErr"
    
}
_checkRequiredVars() {
    log "Verificando ENV Vars obrigatórias ..."
    for var in API_ID API_HASH LOG_CHANNEL_ID DATABASE_URL; do
        test -z ${!var} && quit "Requer $var var !"
    done
    [[ -z $HU_STRING_SESSION && -z $BOT_TOKEN ]] && quit "Necessário HU_STRING_SESSION ou BOT_TOKEN var !"
    [[ -n $BOT_TOKEN && -z $OWNER_ID ]] && quit "Obrigatório OWNER_ID var !"
    test -z $BOT_TOKEN && log "\t[DICA] >>> BOT TOKEN não encontrado! (Desativando o registro avançado)"
}

_checkDefaultVars() {
    replyLastMessage "Verificando ENV Vars padrão ..."
    declare -rA def_vals=(
        [WORKERS]=0
        [PREFERRED_LANGUAGE]="pt"
        [DOWN_PATH]="downloads"
        [UPSTREAM_REMOTE]="upstream"
        [UPSTREAM_REPO]="https://github.com/fnixdev/Kanna-X"
        [LOAD_UNOFFICIAL_PLUGINS]=true
        [CUSTOM_PLUGINS_REPO]=""
        [G_DRIVE_IS_TD]=true
        [CMD_TRIGGER]="."
        [SUDO_TRIGGER]="!"
        [FINISHED_PROGRESS_STR]="█"
        [UNFINISHED_PROGRESS_STR]="░"
    )
    for key in ${!def_vals[@]}; do
        set -a
        test -z ${!key} && eval $key=${def_vals[$key]}
        set +a
    done
    if test $WORKERS -le 0; then
        WORKERS=$(($(nproc)+4))
    elif test $WORKERS -gt 32; then
        WORKERS=32
    fi
    export MOTOR_MAX_WORKERS=$WORKERS
    export HEROKU_ENV=$(test $DYNO && echo 1 || echo 0)
    DOWN_PATH=${DOWN_PATH%/}/
    if [[ $HEROKU_ENV == 1 && -n $HEROKU_API_KEY && -n $HEROKU_APP_NAME ]]; then
        local herokuErr=$(runPythonCode '
import heroku3
try:
    if "'$HEROKU_APP_NAME'" not in heroku3.from_key("'$HEROKU_API_KEY'").apps():
        raise Exception("Invalid HEROKU_APP_NAME \"'$HEROKU_APP_NAME'\"")
except Exception as e:
    print(e)')
        [[ $herokuErr ]] && quit "heroku response > $herokuErr"
    fi
    for var in G_DRIVE_IS_TD LOAD_UNOFFICIAL_PLUGINS; do
        eval $var=$(tr "[:upper:]" "[:lower:]" <<< ${!var})
    done
    local uNameAndPass=$(grep -oP "(?<=\/\/)(.+)(?=\@cluster)" <<< $DATABASE_URL)
    local parsedUNameAndPass=$(runPythonCode '
from urllib.parse import quote_plus
print(quote_plus("'$uNameAndPass'"))')
    DATABASE_URL=$(sed 's/$uNameAndPass/$parsedUNameAndPass/' <<< $DATABASE_URL)
}

_checkDatabase() {
    editLastMessage "Verificando DATABASE_URL ..."
    local mongoErr=$(runPythonCode '
import pymongo
try:
    pymongo.MongoClient("'$DATABASE_URL'").list_database_names()
except Exception as e:
    print(e)')
    [[ $mongoErr ]] && quit "pymongo response > $mongoErr" || log "\tpymongo response > {status : 200}"
}

_checkTriggers() {
    editLastMessage "Verificando TRIGGERS ..."
    test $CMD_TRIGGER = $SUDO_TRIGGER \
        && quit "Invalid SUDO_TRIGGER!, You can't use $CMD_TRIGGER as SUDO_TRIGGER"
}

_checkPaths() {
    editLastMessage "Verificando Paths ..."
    for path in $DOWN_PATH logs; do
        test ! -d $path && {
            log "\tCriando Path : ${path%/} ..."
            mkdir -p $path
        }
    done
}

_checkUpstreamRepo() {
    remoteIsExist $UPSTREAM_REMOTE || addUpstream
    editLastMessage "Buscando dados de UPSTREAM_REPO ..."
    fetchUpstream || updateUpstream && fetchUpstream || quit "UPSTREAM_REPO inválido !"
    fetchBranches
    updateBuffer
}

_setupPlugins() {
    local link path tmp
    if test $(grep -P '^'$2'$' <<< $3); then
        editLastMessage "Clonando $1 Plugins ..."
        link=$(test $4 && echo $4 || echo $3)
        tmp=Temp-Plugins
        gitClone --depth=1 $link $tmp
        replyLastMessage "\tInstalando Requisitos ..."
        upgradePip
        installReq $tmp
        path=$(tr "[:upper:]" "[:lower:]" <<< $1)
        rm -rf kannax/plugins/$path/
        mv $tmp/plugins/ kannax/plugins/$path/
        cp -r $tmp/resources/. resources/
        rm -rf $tmp/
        deleteLastMessage
    else
        editLastMessage "$1 Plugins Desativados !"
    fi
}

_checkUnoffPlugins() {
    _setupPlugins Xtra true $LOAD_UNOFFICIAL_PLUGINS https://github.com/fnixdev/KannaX-Plugins.git
}

_checkCustomPlugins() {
    _setupPlugins Custom "https://([0-9a-f]{40}@)?github.com/.+/.+" $CUSTOM_PLUGINS_REPO
}

_flushMessages() {
    deleteLastMessage
}

assertPrerequisites() {
    _checkBashReq
    _checkPythonVersion
    _checkConfigFile
    _checkRequiredVars
}

assertEnvironment() {
    _checkDefaultVars
    _checkDatabase
    _checkTriggers
    _checkPaths
    _checkUpstreamRepo
    _checkUnoffPlugins
    _checkCustomPlugins
    _ativarlog
    _flushMessages
}
