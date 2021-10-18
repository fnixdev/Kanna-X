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
        [UPSTREAM_REPO]="https://github.com/fnixdev/KannaX"
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
    _flushMessages
}
