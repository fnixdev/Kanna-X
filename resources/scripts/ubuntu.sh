#!/bin/bash
#
# GitHub Repository: https://github.com/fnixdev/KannaX

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
sudo apt-get install tree -y
sudo apt-get install wget2 -y
sudo apt-get install p7zip-full -y
sudo apt-get install jq -y
sudo apt-get install ffmpeg -y
sudo apt-get install wget -y
sudo apt-get install git -y
sudo wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
sudo rm google-chrome-stable_current_amd64.deb
echo "Instalando Python3.9..."
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.9 -y
sudo apt install neofetch -y

echo "Clonando Repositorio."
cd ~
sudo git clone https://github.com/fnixdev/KannaX.git
cd KannaX

echo "Instalando Requisitos do KannaX."
sudo pip install -r requirements.txt
sudo pip3 install -r requirements.txt
sudo cp config.env.sample config.env
echo "Configurando Screen ..."

sudo apt install screen -y
echo "Instalação concluida."