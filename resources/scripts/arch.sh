#!/bin/bash
# 
# By @ffraanks
# GitHub Repository: https://github.com/fnixdev/KannaX

echo "Script de instalação do KannaX by fnixdev"

if [ $(id -u) = 0 ]; then
   echo "Este script não deve ser executado como root ou sudo. Execute normalmente com ./arch.sh. Saindo..."
   exit 1
fi

echo "Escolha uma das opções:"
echo '[1] - sudo'
echo '[2] - doas'
echo
read OPTION

if [ $OPTION == '1' ] || [ $OPTION == '01' ] ; then
  if [ ! -n "`which sudo`" ] ; then
    pacman -Syyu --noconfirm && pacman -S sudo --noconfirm

elif [ $OPTION == '2' ] || [ $OPTION '02' ] ; then
   if [ !-n "`which opendoas`" ] ; then
      pacman -Syyu --noconfirm && pacman -S opendoas --noconfirm
    fi
  fi
fi

sudo pacman -S \
        tree \
        wget \
        p7zip \
        jq \
        ffmpeg \
        wget \
        chromium \
        neofetch \
        python-pymongo \
        python-pip \
        git \
        screen \
        python  --noconfirm

echo "Clonando Repositorio"
cd $HOME
git clone https://github.com/fnixdev/KannaX.git
cd KannaX

echo "Instalando Requisitos do KannaX"
pip3 install -r requirements.txt
cp config.env.sample config.env
echo "Configurando Screen ..."

echo "Instalação Concluída"
cd $HOME/KannaX
