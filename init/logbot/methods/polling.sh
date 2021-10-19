#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

declare -i _to=1
declare -r _input=logs/logbot.stdin

startLogBotPolling() {
    test -z $BOT_TOKEN || _polling &
}

endLogBotPolling() {
    test -z $BOT_TOKEN || echo quit >> $_input
    wait
}

_polling() {
    local cmd func args
    _resetConnection
    log "LogBot Polling Iniciado !"
    while true; do
        cmd="$(head -n 1 $_input 2> /dev/null && sed -i '1d' $_input)"
        test -z "$cmd" && _pollsleep && continue
        test $_to -gt 3 && let _to-=3
        case $cmd in
            quit)
                break;;
            deleteLastMessage|printMessages|deleteMessages)
                $cmd;;
            sendMessage*|replyLastMessage*|editLastMessage*)
                func=$(echo $cmd | cut -d' ' -f1)
                args=$(echo $cmd | cut -d' ' -f2-)
                $func "~$args";;
            *)
                log "unknown : < $cmd >"
                test -z $cmd && break;;
        esac
        sleep 1
    done
    log "LogBot Polling Finalizado !"
    _resetConnection
    exit 0
}

_resetConnection() {
    rm -f $_input
}

_pollsleep() {
    let _to+=1
    log "sleeping (${_to}s) (caused by \"LogBot.polling\")"
    sleep $_to
}
