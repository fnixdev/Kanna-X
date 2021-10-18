# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

__all__ = ['Conversation']

from typing import Union

from ... import types


class Conversation:  # pylint: disable=missing-class-docstring
    def conversation(self,
                     chat_id: Union[str, int],
                     *, user_id: Union[str, int] = 0,
                     timeout: Union[int, float] = 10,
                     limit: int = 10) -> 'types.new.Conversation':
        """\nIsso retorna um novo objeto de conversa.

        Parameters:
            chat_id (``int`` | ``str``):
                Identificador único (int) ou nome de usuário (str) do chat de destino.
                Para sua nuvem pessoal (mensagens salvas)
                você pode simplesmente usar "me" ou "self".
                Para um contato que existe em sua lista de endereços do Telegram
                você pode usar seu número de telefone (str).

            user_id (``int`` | ``str`` | , *optional*):
                definir um usuário específico neste chat.

            timeout (``int`` | ``float`` | , *optional*):
                definir o tempo limite da conversa.
                o padrão é 10.

            limit (``int`` | , *optional*):
                definir limite de mensagem de conversa.
                o padrão é 10.
        """
        return types.new.Conversation(self, chat_id, user_id, timeout, limit)
