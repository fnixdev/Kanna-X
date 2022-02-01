#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

. init/logbot/logbot.sh
. init/utils.sh
. init/checks.sh

trap handleSigTerm TERM
trap handleSigInt INT
trap 'echo hi' USR1

initKannaX() {
    printLogo
    assertPrerequisites
    sendMessage "Inicializando KannaX ..."
    assertEnvironment
    editLastMessage "Iniciando KannaX ..."
    printLine
}

startKannaX() {
    startLogBotPolling
    runPythonModule kannax "$@"
}

stopKannaX() {
    sendMessage "Finalizando KannaX ..."
    endLogBotPolling
}

handleSigTerm() {
    log "Saindo com SIGTERM (143) ..."
    stopKannaX
    exit 143
}

handleSigInt() {
    log "Saindo com SIGINT (130) ..."
    stopKannaX
    exit 130
}

runKannaX() {
    initKannaX
    startKannaX "$@"
    local code=$?
    stopKannaX
    return $code
}
