#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

raw.getMessageCount() {
    return ${#_allMessages[@]}
}

raw.getAllMessages() {
    echo ${_allMessages[@]}
}

raw.getLastMessage() {
    if test ${#_allMessages[@]} -gt 0; then
        ${_allMessages[-1]}.$1 "$2"
    elif [[ -n $BOT_TOKEN && -n $LOG_CHANNEL_ID ]]; then
        log "first sendMessage ! (caused by \"core.methods.$FUNCNAME\")\n"$2""
    else
        log "$2"
    fi
}
