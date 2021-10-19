import asyncio
from os import system
from time import time

from git import Repo
from git.exc import GitCommandError

from kannax import Config, Message, get_collection, pool, kannax
from kannax.utils import runcmd

LOG = kannax.getLogger(__name__)
CHANNEL = kannax.getCLogger(__name__)

FROZEN = get_collection("FROZEN")


async def _init():
    start = kannax.uptime
    if start == "0h, 0m, 1s":
        await CHANNEL.log("Bot iniciado...")


@kannax.on_cmd(
    "update",
    about={
        "header": "Verifica se há atualizações",
        "flags": {
            "-pull": "pull updates",
            "-branch": "Padrão é -master",
            "-pr": "Verifica att dos Plugins Xtras",
            "-prp": "Faz pull das atts do Xtra Plugins",
        },
        "uso": (
            "{tr}update : verificar atualizações do branch padrão\n"
            "{tr}update -[branch_name] : verifique as atualizações de qualquer branch\n"
            "use -pull para atualizar\n"
        ),
        "examples": "{tr}update -pull",
    },
    del_pre=True,
    allow_channels=False,
)
async def check_update(message: Message):
    """check or do updates"""
    await message.edit("`Verificando atualizações, por favor aguarde....`")
    if Config.HEROKU_ENV:
        await message.edit(
            "__Hey hey, me parece que você esta usando Heroku, as atulizações por aqui foram desativadas por questões de segurança__\n"
            "__Nâo se precoupe, seu bot será atualizado automaticamente quando o Heroku reiniciar__"
        )
        return
    flags = list(message.flags)
    pull_from_repo = False
    push_to_heroku = False
    branch = "master"
    u_repo = Config.UPSTREAM_REPO
    u_repo = u_repo.replace("/", " ")
    git_u_n = u_repo.split()[2]
    if "pull" in flags:
        pull_from_repo = True
        flags.remove("pull")
    if "push" in flags:
        if not Config.HEROKU_APP:
            await message.err("HEROKU APP : Não foi encontrado!")
            return
        # push_to_heroku = True
        # flags.remove("push")
    if "pr" in flags:
        branch = "master"
        out = _get_updates_pr(git_u_n, branch)
    if "prp" in flags:
        await message.edit("`Atualizando o os Plugins...`", log=__name__)
        await runcmd("bash run")
        asyncio.get_event_loop().create_task(kannax.restart())
    if len(flags) == 1:
        branch = flags[0]
    repo = Repo()
    if branch not in repo.branches:
        await message.err(f"invalid branch name : {branch}")
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
                    "**KannaX foi atualizado!**\n"
                    "`Reiniciando... Aguarde um pouco!`",
                )
                asyncio.get_event_loop().create_task(kannax.restart(True))
        elif push_to_heroku:
            await _pull_from_repo(repo, branch)
        else:
            active = repo.active_branch.name
            if active == branch:
                await message.err(f"ja esta em [{branch}]!")
                return
            await message.edit(
                f"`Moving HEAD from [{active}] >>> [{branch}] ...`", parse_mode="md"
            )
            await _pull_from_repo(repo, branch)
            await CHANNEL.log(f"`Moved HEAD from [{active}] >>> [{branch}] !`")
            await message.edit("`Now restarting... Wait for a while!`", del_in=3)
            asyncio.get_event_loop().create_task(kannax.restart())
    if push_to_heroku:
        await _push_to_heroku(message, repo, branch)


def _get_updates(repo: Repo, branch: str) -> str:
    repo.remote(Config.UPSTREAM_REMOTE).fetch(branch)
    upst = Config.UPSTREAM_REPO.rstrip("/")
    out = ""
    upst = Config.UPSTREAM_REPO.rstrip("/")
    for i in repo.iter_commits(f"HEAD..{Config.UPSTREAM_REMOTE}/{branch}"):
        out += f"**#{i.count()}** : [{i.summary}]({upst}/commit/{i}) 🧙🏻‍♂️ __{i.author}__\n\n"
    return out


def _get_updates_pr(git_u_n: str, branch: str) -> str:
    pr_up = f"https://github.com/{git_u_n}/KannaX-Plugins"
    repo = Repo()
    repo.remote(pr_up).fetch(branch)
    upst = pr_up.rstrip("/")
    out = ""
    upst = pr_up.rstrip("/")
    for i in repo.iter_commits(f"HEAD..{pr_up}/{branch}"):
        out += f"**#{i.count()}** : [{i.summary}]({upst}/commit/{i}) 🧙🏻‍♂️ __{i.author}__\n\n"
    return out


async def _pull_from_repo(repo: Repo, branch: str) -> None:
    await FROZEN.drop()
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