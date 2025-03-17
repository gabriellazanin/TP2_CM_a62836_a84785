from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board_list import BoardList
import itertools
import flet as ft
from data_store import DataStore


class Item(ft.Container):
    id_counter = itertools.count()

    def __init__(self, list: "BoardList", store: DataStore, item_text: str):
        self.item_id = next(Item.id_counter)
        self.store: DataStore = store
        self.list = list
        self.item_text = item_text
        
        self.edit_button = ft.IconButton(ft.Icons.EDIT, on_click=self.edit_card)
        
        self.card_item = ft.Card(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Checkbox(label=f"{self.item_text}", width=200),
                        border_radius=ft.border_radius.all(5),
                    ),
                    ft.Row([
                        self.edit_button,
                        ],
                        alignment = ft.alignment.center_right,
                    ),
                ],
                width=200,
                wrap=True,
            ),
            elevation=1,
            data=self.list,
        )
        self.view = ft.Draggable(
            group="items",
            content=ft.DragTarget(
                group="items",
                content=self.card_item,
                on_accept=self.drag_accept,
                on_leave=self.drag_leave,
                on_will_accept=self.drag_will_accept,
            ),
            data=self,
        )
        super().__init__(content=self.view)

    def drag_accept(self, e):
        src = self.page.get_control(e.src_id)

        # skip if item is dropped on itself
        if src.content.content == e.control.content:
            self.card_item.elevation = 1
            self.list.set_indicator_opacity(self, 0.0)
            e.control.update()
            return

        # item dropped within same list but not on self
        if src.data.list == self.list:
            self.list.add_item(chosen_control=src.data, swap_control=self)
            self.card_item.elevation = 1
            e.control.update()
            return

        # item added to different list
        self.list.add_item(src.data.item_text, swap_control=self)
        # remove from the list to which draggable belongs
        src.data.list.remove_item(src.data)
        self.list.set_indicator_opacity(self, 0.0)
        self.card_item.elevation = 1
        self.page.update()

    def drag_will_accept(self, e):
        if e.data == "true":
            self.list.set_indicator_opacity(self, 1.0)
        self.card_item.elevation = 20 if e.data == "true" else 1
        self.page.update()

    def drag_leave(self, e):
        self.list.set_indicator_opacity(self, 0.0)
        self.card_item.elevation = 1
        self.page.update()
        
    def edit_card(self, e):
        def save_card(e):
            self.item_text = edit_field.value  # Captura o novo texto
            self.store.update_item(self.list.board_list_id, self.item_id, self.item_text)
            self.card_item.content.controls[0].label = self.item_text

            self.list.update_list_item(self.item_id)
            self.page.update()
            self.page.close(dialog)
                    
        edit_field = ft.TextField(value=self.item_text, on_submit=save_card)
        dialog = ft.AlertDialog(
            title=ft.Text("Edit Card"),
            content=edit_field,
            actions=[ft.TextButton("Save", on_click=save_card)]
        )
        self.page.open(dialog)
        
            