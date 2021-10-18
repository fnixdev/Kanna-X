#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

Message() {
    . <(sed "s/_Message/$1/g" init/logbot/core/types/messageClass.sh)
}
