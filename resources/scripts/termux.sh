#!/bin/bash

log() {
    echo -e "\n$1\n########################\n"
}

status() {
    printf "Installing : [${1}] ...\n"
}

prog() {
    let _prog=${1}
    let _done=($_prog*4)/10
    let _left=40-$_done
    _fill=$(printf "%${_done}s")
    _empty=$(printf "%${_left}s")
    printf "Progress : ${_fill// /▰}${_empty// /▱} $_prog%%\n"
}

pkg_update() {
    prog 0
    pkg update -y
    prog 1
    pkg upgrade -y
}

pkg_install() {
    status ${1}
    prog ${2}
    pkg install -y ${1} &> /dev/null
}

pip_install() {
    status ${1}
    prog ${2}
    CFLAGS="-O0" pip install -U ${1} 1> /dev/null
}

log "Updating Packages"
pkg_update
pkg_install root-repo 3

log "Installing Necessary Packages"
pkg_install python 5
pip_install pip 10
pip_install wheel 15
pip_install setuptools 20
pkg_install git 25
pkg_install jq 30
pkg_install proot 32
pkg_install resolv-conf 34
pkg_install libxml2 36
pkg_install libxslt 38
pkg_install libjpeg-turbo 40

status "pillow"
prog 45
LDFLAGS="-L/system/lib/" CFLAGS="-I/data/data/com.termux/files/usr/include/" \
    pip install -U Pillow 1> /dev/null

log "Clonning Repository"
prog 50
rm -rf Userge
git clone https://github.com/fnixdev/Kanna-X Kanna-X &> /dev/null
cd Kanna-X

log "Installing Requirements"
let _val=55
while IFS= read -r line
do
    [[ ${line,,} == "pillow"* ]] && continue
    pip_install $line $_val
    let _val+=1
done < "requirements.txt"

cp config.env.sample config.env
echo -e "\nInstallation Completed !\n"
prog 100
log "Wait. Now openning config.env ...\nEdit, and Save (ctrl+s) and Close (ctrl+x) it."
sleep 10
nano config.env

log "All done!\nNow run command \"termux-chroot\" and \"cd Userge && bash run\" respectively.\nEnjoy :)"
echo -e "\nFor more info: https://theuserge.github.io/termux\n"
