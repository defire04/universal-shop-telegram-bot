from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from data.config import BLOCKED_USER_IDS


class SimpleBlockedUsersMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user = event.from_user

        if user and user.id in BLOCKED_USER_IDS:
            if isinstance(event, Message):
                await event.answer("⛔ Доступ заблоковано.")
                return None

            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ Доступ заблоковано.", show_alert=True)
                return None

        return await handler(event, data)
