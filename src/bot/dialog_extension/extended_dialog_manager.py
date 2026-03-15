from aiogram import Bot
from aiogram.types import Chat, Message
from aiogram_dialog import DialogManager, ShowMode

from .dialog_wrapper import DialogManagerWrapper
from .extended_fsm_context import ExtendedFSMContext, extend_fsm_context


class ExtendedDialogManager(DialogManagerWrapper):
    @property
    def state(self) -> ExtendedFSMContext:
        return extend_fsm_context(self.middleware_data["state"])

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
            print(f"clear_messages could not delete {len(to_delete_list)} messages, {e}")
        await self.state.set_to_delete_list([])

    async def switch_to_current(self, show_mode: ShowMode = ShowMode.AUTO):
        return await self.switch_to(self.current_context().state, show_mode=show_mode)

    async def answer_and_track(self, text: str, **kwargs):
        to_delete = await self.bot.send_message(chat_id=self.chat.id, text=text, **kwargs)
        await self.track_message(to_delete)

    async def answer_and_retry(self, text: str, **kwargs):
        to_delete = await self.bot.send_message(chat_id=self.chat.id, text=text, **kwargs)
        await self.track_message(to_delete)
        await self.switch_to_current(ShowMode.DELETE_AND_SEND)


def extend_dialog(dialog_manager: DialogManager) -> ExtendedDialogManager:
    if not isinstance(dialog_manager, ExtendedDialogManager):
        dialog_manager = ExtendedDialogManager(dialog_manager)
    return dialog_manager
