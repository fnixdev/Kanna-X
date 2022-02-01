# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Editado por fnixdev

__all__ = ['SendReadAcknowledge']

from typing import List, Optional, Union

from pyrogram.raw import functions

from ...ext import RawClient, RawMessage


class SendReadAcknowledge(RawClient):  # pylint: disable=missing-class-docstring
    async def send_read_acknowledge(self,
                                    chat_id: Union[int, str],
                                    message: Union[List[RawMessage],
                                                   Optional[RawMessage]] = None,
                                    *, max_id: Optional[int] = None,
                                    clear_mentions: bool = False) -> bool:
        """\nMarca as mensagens como lidas e, opcionalmente, limpa as menções.

        Parameters:
            chat_id (``int`` | ``str``):
                Identificador único (int) ou nome de usuário (str) do chat de destino.
                 Para sua nuvem pessoal (mensagens salvas)
                 você pode simplesmente usar "me" ou "self".
                 Para um contato que existe em sua lista de endereços do Telegram
                 você pode usar seu número de telefone (str).

            message (``list`` | :obj: `Message`, *optional*):
                Uma lista de mensagens ou uma única mensagem.

            max_id (``int``, *optional*):
                Até que mensagem deve ser enviada a confirmação de leitura.
                Isso tem prioridade sobre o parâmetro `` message``.

            clear_mentions (``bool``, *optional*):
                Se o símbolo de menção deve ser limpo (para que
                não há mais menções) ou não para a entidade em questão.
                Se nenhuma mensagem for fornecida, esta será a única ação
                ocupado.
                o padrão é False.

        Returns:
            Em caso de sucesso, True é retornado.
        """
        if max_id is None:
            if message:
                if isinstance(message, list):
                    max_id = max(msg.message_id for msg in message)
                else:
                    max_id = message.message_id
            else:
                max_id = 0
        if clear_mentions:
            await self.send(
                functions.messages.ReadMentions(
                    peer=await self.resolve_peer(chat_id)))
            if max_id is None:
                return True
        if max_id is not None:
            return bool(await self.read_history(chat_id=chat_id, max_id=max_id))
        return False
