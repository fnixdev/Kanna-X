import asyncio
from os import system
from time import time

from git import Repo
from git.exc import GitCommandError

from kannax import Config, Message, pool, kannax

LOG = kannax.getLogger(__name__)
CHANNEL = kannax.getCLogger(__name__)


@kannax.on_cmd(
    "update",
    about={
        "header": "Verifique as atualizações ou atualize o KannaX",
        "flags": {
            "-pull": "puxar atualizações",
            "-branch": "Padrão é -master",
        },
        "uso": (
            "{tr}update : verificar atualizações do branch padrão\n"
            "{tr}update -[branch_name] : verifique as atualizações de qualquer branch\n"
            "use -pull para atualizar\n"
        ),
        "exemplos": "{tr}update -pull",
    },
    del_pre=True,
    allow_channels=False,
)
async def check_update(message: Message):
    """verificar ou fazer atualizações"""
    await message.edit("`Verificando atualizações, por favor aguarde....`")
    if Config.HEROKU_ENV:
        await message.edit(
            "**Heroku App detectado !**, As atualizações foram desativadas por segurança.\n"
            "Seu bot será atualizado automaticamente quando o Heroku reiniciar"
        )
        return
    flags = list(message.flags)
    pull_from_repo = False
    push_to_heroku = False
    branch = "master"
    if "pull" in flags:
        pull_from_repo = True
        flags.remove("pull")
    if "push" in flags:
        if not Config.HEROKU_APP:
            await message.err("HEROKU APP : Não pode ser encontrado !")
            return
        # push_to_heroku = True
        # flags.remove("push")
    if len(flags) == 1:
        branch = flags[0]
    repo = Repo()
    if branch not in repo.branches:
        await message.err(f"nome da branch inválida : {branch}")
        return
    try:
        out = _get_updates(repo, branch)
    except GitCommandError as g_e:
        if "128" in str(g_e):
            system(
                f"git fetch {Config.UPSTREAM_REMOTE} {branch} && git checkout -f {branch}"
            )
            out = _get_updates(repo, branch)
        else:
            await message.err(g_e, del_in=5)
            return
    if not (pull_from_repo or push_to_heroku):
        if out:
            change_log = (
                f"**Novas atualizações encontradas para KannaX\nDigite `{Config.CMD_TRIGGER}update -pull` para atualizar\n\n✨ ALTERAÇÕES**\n\n"
            )
            await message.edit_or_send_as_file(
                change_log + out, disable_web_page_preview=True
            )
        else:
            await message.edit(f"**Seu KannaX ja esta atualizado**", del_in=5)
        return
    if pull_from_repo:
        if out:
            await message.edit(f"`Novas atualizações encontradas para KannaX, Atualizando...`")
            await _pull_from_repo(repo, branch)
            await CHANNEL.log(
                f"**Atualização concluida.\n\n✨ ALTERAÇÕES**\n\n{out}"
            )
            if not push_to_heroku:
                await message.edit(
                    "**KannaX Atualizado com Sucesso!**\n"
                    "`Reiniciando... Aguarde um pouco!`",
                    del_in=0,
                )
                asyncio.get_event_loop().create_task(kannax.restart(hard=True))
        elif push_to_heroku:
            await _pull_from_repo(repo, branch)
        else:
            active = repo.active_branch.name
            if active == branch:
                await message.err(f"ja esta em [{branch}]!")
                return
            await message.edit(
                f"`Movendo HEAD de [{active}] >>> [{branch}] ...`", parse_mode="md"
            )
            await _pull_from_repo(repo, branch)
            await CHANNEL.log(f"`Moveu HEAD de [{active}] >>> [{branch}] !`")
            await message.edit("`Reiniciando... Aguarde um pouco!`", del_in=3)
            asyncio.get_event_loop().create_task(kannax.restart(hard=True))
    if push_to_heroku:
        await _push_to_heroku(message, repo, branch)


def _get_updates(repo: Repo, branch: str) -> str:
    repo.remote(Config.UPSTREAM_REMOTE).fetch(branch)
    upst = Config.UPSTREAM_REPO.rstrip("/")
    out = ""
    upst = Config.UPSTREAM_REPO.rstrip("/")
    for i in repo.iter_commits(f"HEAD..{Config.UPSTREAM_REMOTE}/{branch}"):
        out += f"**#{i.count()}** : [{i.summary}](https://t.me/kannaxup) 🧙🏻‍♂️ __{i.author}__\n\n"
    return out


async def _pull_from_repo(repo: Repo, branch: str) -> None:
    repo.git.checkout(branch, force=True)
    repo.git.reset("--hard", branch)
    repo.remote(Config.UPSTREAM_REMOTE).pull(branch, force=True)
    await asyncio.sleep(1)


async def _push_to_heroku(msg: Message, repo: Repo, branch: str) -> None:
    sent = await msg.edit(
        f"`Enviando atualizações de [{branch}] para o heroku...\n"
        "isso vai demorar até 5 min`\n\n"
        f"* **Reiniciar** após 5 min usando `{Config.CMD_TRIGGER}restart -h`\n\n"
        "* Depois de reiniciado com sucesso, verifique as atualizações novamente :)"
    )
    try:
        await _heroku_helper(sent, repo, branch)
    except GitCommandError as g_e:
        LOG.exception(g_e)
    else:
        await sent.edit(
            f"**HEROKU APP : {Config.HEROKU_APP.name} esta atualizado em [{branch}]**"
        )


@pool.run_in_thread
def _heroku_helper(sent: Message, repo: Repo, branch: str) -> None:
    start_time = time()
    edited = False

    def progress(op_code, cur_count, max_count=None, message=""):
        nonlocal start_time, edited
        prog = f"**code:** `{op_code}` **cur:** `{cur_count}`"
        if max_count:
            prog += f" **max:** `{max_count}`"
        if message:
            prog += f" || `{message}`"
        LOG.debug(prog)
        now = time()
        if not edited or (now - start_time) > 3 or message:
            edited = True
            start_time = now
            kannax.loop.create_task(sent.try_to_edit(f"{cur_msg}\n\n{prog}"))

    cur_msg = sent.text.html
    repo.remote("heroku").push(
        refspec=f"{branch}:master", progress=progress, force=True
    )
