#!/bin/bash
#
# GitHub Repository: https://github.com/fnixdev/Kanna-X

echo "Script de instalação do KannaX by fnixdev"

if [ $(id -u) = 0 ]; then
   echo "Este script não deve ser executado como root ou sudo. Execute normalmente com ./ubuntu.sh.  Saindo..."
   exit 1
fi

# Instalando dependencias
echo "Instalando Dependencias.."
if [ ! -n "`which sudo`" ]; then
  apt-get update && apt-get install sudo -y
fi

sudo apt-get update -y
sudo apt-get install tree wget2 p7zip-full jq ffmpeg wget git neofetch mediainfo -y
sudo wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
sudo rm google-chrome-stable_current_amd64.deb

echo "Instalando Python3.9..."
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.9 -y
sudo apt install python3-pip

echo "Clonando Repositorio."
cd ~
sudo git clone https://github.com/fnixdev/Kanna-X.git
cd Kanna-X

echo "Instalando Requisitos do KannaX."
sudo pip3 install -r requirements.txt

echo "Configurando Screen ..."

sudo apt install screen -y
echo "Instalação concluida."
