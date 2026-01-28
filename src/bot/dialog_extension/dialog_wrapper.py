from typing import Any

from aiogram.fsm.state import State
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import AccessSettings, ChatEvent, Context, Stack, StartMode
from aiogram_dialog.api.protocols.manager import BaseDialogManager, UnsetId


class DialogManagerWrapper(DialogManager):
    original: DialogManager

    def __init__(self, dialog_manager: DialogManager):
        self.original = dialog_manager

    async def done(self, result: Any = None, show_mode: ShowMode | None = None) -> None:
        return await self.original.done(result, show_mode)

    async def start(
        self,
        state: State,
        data: dict | list | int | str | float | None = None,
        mode: StartMode = StartMode.NORMAL,
        show_mode: ShowMode | None = None,
        access_settings: AccessSettings | None = None,
    ) -> None:
        return await self.original.start(state, data, mode, show_mode, access_settings)

    async def switch_to(self, state: State, show_mode: ShowMode | None = None) -> None:
        return await self.original.switch_to(state, show_mode)

    async def update(self, data: dict, show_mode: ShowMode | None = None) -> None:
        return await self.original.update(data, show_mode)

    def bg(
        self,
        user_id: int | None = None,
        chat_id: int | None = None,
        stack_id: str | None = None,
        thread_id: int | None | UnsetId = UnsetId.UNSET,
        business_connection_id: str | None | UnsetId = UnsetId.UNSET,
        load: bool = False,
    ) -> BaseDialogManager:
        return self.original.bg(user_id, chat_id, stack_id, thread_id, business_connection_id, load)

    @property
    def event(self) -> ChatEvent:
        return self.original.event

    async def mark_closed(self) -> None:
        return await self.original.mark_closed()

    @property
    def middleware_data(self) -> dict:
        return self.original.middleware_data

    @property
    def dialog_data(self) -> dict:
        return self.original.dialog_data

    @property
    def start_data(self) -> dict | list | int | str | float | None:
        return self.original.start_data

    @property
    def show_mode(self) -> ShowMode:
        return self.original.show_mode

    @show_mode.setter
    def show_mode(self, show_mode: ShowMode) -> None:
        self.original.show_mode = show_mode

    def is_preview(self) -> bool:
        return self.original.is_preview()

    async def show(self, show_mode: ShowMode | None = None) -> None:
        return await self.original.show(show_mode)

    async def answer_callback(self) -> None:
        return await self.original.answer_callback()

    def current_context(self) -> Context:
        return self.original.current_context()

    def has_context(self) -> bool:
        return self.original.has_context()

    def current_stack(self) -> Stack:
        return self.original.current_stack()

    async def next(self, show_mode: ShowMode | None = None) -> None:
        return await self.original.next(show_mode)

    async def back(self, show_mode: ShowMode | None = None) -> None:
        return await self.original.back(show_mode)

    def find(self, widget_id) -> Any | None:
        return self.original.find(widget_id)

    async def reset_stack(self, remove_keyboard: bool = True) -> None:
        return await self.original.reset_stack(remove_keyboard)

    async def load_data(self) -> dict:
        return await self.original.load_data()

    async def close_manager(self) -> None:
        return await self.original.close_manager()
