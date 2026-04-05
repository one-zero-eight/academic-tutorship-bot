from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import List


class UnpackedList(List):
    """Inherited from List widget, but unpacking item dict for compatibility with fluent formatting in i18n strings"""

    async def _render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        items = self.items_getter(data)
        pages = self._get_page_count(items)
        if self.page_size is None:
            current_page = 0
            start = 0
        else:
            last_page = pages - 1
            current_page = min(last_page, await self.get_page(manager))
            start = current_page * self.page_size
            items = items[start : start + self.page_size]

        texts = [
            await self.field.render_text(
                {
                    "current_page": current_page,
                    "current_page1": current_page + 1,
                    "pages": pages,
                    "data": data,
                    "pos": pos + 1,
                    "pos0": pos,
                    **item,  # NOTE: unpacking item dict for compatibility with fluent formatting in i18n strings
                },
                manager,
            )
            for pos, item in enumerate(items, start)
        ]
        return "\n".join(texts)
