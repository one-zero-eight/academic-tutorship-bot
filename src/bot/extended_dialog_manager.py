from aiogram import Bot, Router
from aiogram.types import Chat, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.protocols import DialogRegistryProtocol
from aiogram_dialog.context.media_storage import MediaIdStorage
from aiogram_dialog.manager.manager import ManagerImpl
from aiogram_dialog.manager.manager_factory import DefaultManagerFactory
from aiogram_dialog.manager.message_manager import MessageManager

from src.bot.dto import *

from .extended_fsm_context import ExtendedFSMContext
from .extended_fsm_context import extend as extend_context


class ExtendedDialogManager(ManagerImpl):
    @staticmethod
    def wrap(dialog_manager) -> "ExtendedDialogManager":
        return ExtendedDialogManager(
            event=dialog_manager.event,
            message_manager=dialog_manager.message_manager,
            media_id_storage=dialog_manager.media_id_storage,
            registry=dialog_manager._registry,
            router=dialog_manager._router,
            data=dialog_manager._data,
        )

    @property
    def state(self) -> ExtendedFSMContext:
        return extend_context(self.middleware_data["state"])

    @property
    def bot(self) -> Bot:
        return self.middleware_data["bot"]

    @property
    def chat(self) -> Chat:
        return self.middleware_data["event_chat"]

    async def track_message(self, message: Message):
        """Track messages to delete later ("to_delete_list" in state)"""
        await self.state.add_to_delete(message)

    async def clear_messages(self):
        """Delete tracked messages ("to_delete_id" in state)"""
        to_delete_list = await self.state.get_to_delete_list()
        print("TRYING TO CLEAR:", to_delete_list)
        try:
            await self.bot.delete_messages(self.chat.id, to_delete_list)
        except Exception as e:
            return print(f"clear_messages could not delete {len(to_delete_list)} messages, {e}")
        await self.state.set_to_delete_list([])

    async def switch_to_current(self, show_mode: ShowMode):
        return await self.switch_to(self.current_context().state, show_mode=ShowMode.DELETE_AND_SEND)

    async def answer_and_track(self, text: str, **kwargs):
        to_delete = await self.bot.send_message(chat_id=self.chat.id, text=text, **kwargs)
        await self.track_message(to_delete)

    async def answer_and_retry(self, text: str, **kwargs):
        to_delete = await self.bot.send_message(chat_id=self.chat.id, text=text, **kwargs)
        await self.track_message(to_delete)
        await self.switch_to_current(ShowMode.DELETE_AND_SEND)


class ExtendedDialogManagerFactory(DefaultManagerFactory):
    @staticmethod
    def defaults() -> "ExtendedDialogManagerFactory":
        return ExtendedDialogManagerFactory(
            media_id_storage=MediaIdStorage(),
            message_manager=MessageManager(),
        )

    def __call__(
        self,
        event: ChatEvent,
        data: dict,
        registry: DialogRegistryProtocol,
        router: Router,
    ) -> DialogManager:
        return ExtendedDialogManager(
            event=event,
            data=data,
            message_manager=self.message_manager,
            media_id_storage=self.media_id_storage,
            registry=registry,
            router=router,
        )


def extend(dialog_manager: DialogManager) -> ExtendedDialogManager:
    if not isinstance(dialog_manager, ExtendedDialogManager):
        dialog_manager = ExtendedDialogManager.wrap(dialog_manager)
    return dialog_manager
