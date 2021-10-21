#!/bin/bash

# By @ffraanks and @Luska1331
# GitHub Repository: https://github.com/fnixdev/Kanna-X

PacoteExiste() {
    if pacman -Qs $1 > /dev/null; then
        echo " → [✔] - $1 esta instalando."
        return 0
    else
        echo " → [⚠] - $1 não esta instalado."
        return 1
    fi
}

echo "★ - Script de instalação do KannaX - ★"

sleep 2

if [ $(id -u) = 0 ]; then
   echo "[⚠] - Este script não deve ser executado como root ou sudo. Execute com bash arch.sh. Saindo..."
   exit 1
fi

if PacoteExiste sudo > /dev/null ; then
    echo "[★] - Sudo foi encontrado!"
elif PacoteExiste doas > /dev/null ; then
    echo "[★] - Doas foi encontrado!"
else
    echo "[⚠] - Não foi encontrado nenhum pacote para root, irei instalar o sudo por padrão"
    pacman -Sy sudo --noconfirm
fi

cmd="sudo pacman -Sy"

packages="tree wget p7zip jq ffmpeg wget chromium neofetch python-pymongo python-pip git screen python"

echo "[★] - Verificando os pacotes requiridos:"

count=0
for package in $packages ; do
    if PacoteExiste $package ; then
        true
    else
        cmd="$cmd $package"
        count=$((count+1))
    fi
done

if ! [ $count -eq 0 ] ; then
    echo "[⚠] - Estão faltando $count pacotes, espere para instalar eles..."
    eval $cmd
else
    echo "[✔] - Todos os pacotes estão devidamente instalados."
fi

cd $HOME

if [ -d "$HOME/Kanna-X" ] ; then
    echo "[★] - O pasta \"Kanna-X\" ja existe!"
else
    echo "[★] - Clonando a Kanna-X em \"$HOME\""
    git clone https://github.com/fnixdev/Kanna-X.git
fi

cd Kanna-X

if [ -d "$HOME/Kanna-X/kannax-venv" ] ; then
    echo "[★] - A venv KannaX-Venv ja existe"
else
    {
        echo "[★] - Criando a venv KannaX-Venv e instalando os requirimentos."
        python -m venv kannax-venv
        echo "[✔] - Virtual Env foi criada com sucesso!"
        source $HOME/Kanna-X/kannax-venv/bin/activate
        echo "[★] - Instalando os requirimentos da KannaX!"
        pip install -r requirements.txt
        echo "[✔] - Requirimentos instalados com sucesso."
    } || {
        echo "[⚠] - Não foi possivel criar a Virtual Env."
        exit 1
    }
fi

if [ -d "$HOME/Kanna-X/config.env.sample" ] ; then
    echo "[★] - Renomeando o arquivo \"config.env.sample\" para \"config.env\""
    echo "[★] - Por favor, abra o arquivo \"config.env\" e configure as Vars."
    cp config.env.sample config.env > /dev/null
else
    printf "[★] - O arquivo \"config.env\" ja existe! Verifique se esta tudo configurado."
fi

printf "\n[✔] - Download completo, basta apenas configurar o \"config.env\", tenha um bot uso do seu Kanna-X!\n"

