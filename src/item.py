from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board_list import BoardList
import itertools
import flet as ft
from data_store import DataStore


class Item(ft.Container):
    id_counter = itertools.count()

    def __init__(self, list: "BoardList", store: DataStore, item_text: str, labels=None):
        self.item_id = next(Item.id_counter)
        self.store: DataStore = store
        self.list = list
        self.item_text = item_text
        self.labels = labels or []
        
        self.edit_button = ft.IconButton(ft.Icons.EDIT, on_click=self.edit_card)
        self.delete_button = ft.IconButton(ft.Icons.DELETE, on_click=self.delete_card)
        
        self.add_label_button = ft.IconButton(ft.Icons.LABEL, on_click=self.add_label)
        self.labels_view = ft.Row(
            [self.create_label_view(label) for label in self.labels],
            spacing=5
        )
        
        self.card_item = ft.Card(
            content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Checkbox(label=f"{self.item_text}", width=200),
                                border_radius=ft.border_radius.all(5),
                            ),self.labels_view,
                            ft.Row([
                                self.edit_button,
                                self.delete_button,
                                self.add_label_button,
                            ],
                            alignment=ft.alignment.center_right),
                        ],
                        spacing=5,
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
            new_text = edit_field.value
            if new_text:
                self.item_text = new_text
                self.store.update_item(self.list.board_list_id, self.item_id, new_text)
                
                checkbox = self.card_item.content.controls[0].content 
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.label = new_text  
                    
                self.page.update()
                self.page.close(dialog)
                self.page.update()                    
        edit_field = ft.TextField(value=self.item_text, on_submit=save_card)
        dialog = ft.AlertDialog(
            title=ft.Text("Edit Card"),
            content=edit_field,
            actions=[ft.TextButton("Save", on_click=save_card)]
        )
        self.page.open(dialog)
        
    def create_label_view(self, label):
        return ft.Container(
            content=ft.Row([
                ft.Text(label["text"], color=ft.Colors.WHITE, weight="bold"), 
                ft.IconButton(ft.Icons.CLOSE, icon_size=12, on_click=lambda e, lbl=label: self.remove_label(lbl))
            ]),
            bgcolor=label["color"], 
            border_radius=ft.border_radius.all(5),
            padding=ft.padding.symmetric(horizontal=5, vertical=1),
        )


    def add_label(self, e):
        label_colors = {
            "Red": ft.Colors.RED_200,
            "Green": ft.Colors.GREEN_200,
            "Orange": ft.Colors.AMBER_300,
            "Purple": ft.Colors.DEEP_PURPLE_200,
        }

        selected_color = [ft.Colors.BLUE_500]  # Cor padrão

        def set_color(e):
            selected_color[0] = e.control.data
            for option in color_select.controls:
                option.border = ft.border.all(3, ft.Colors.BLACK26) if option.data == selected_color[0] else None
            dialog.content.update()

        color_select = ft.Row(
            [
                ft.Container(
                    bgcolor=color,
                    width=30,
                    height=30,
                    border_radius=ft.border_radius.all(5),
                    data=color,
                    on_click=set_color,
                )
                for _, color in label_colors.items()
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        def save_label(e):
            new_label_text = label_field.value.strip()
            if new_label_text:
                new_label = {"text": new_label_text, "color": selected_color[0]}
                self.labels.append(new_label)

                self.labels_view.controls.append(self.create_label_view(new_label))
                self.store.update_item(self.list.board_list_id, self.item_id, self.item_text, self.labels)
                self.page.update()
                self.page.close(dialog)

        label_field = ft.TextField(label="New Label", on_submit=save_label)
        dialog = ft.AlertDialog(
            title=ft.Text("Add Label"),
            content=ft.Column(
                [
                    label_field,
                    ft.Text("Choose a color:", weight="bold"),
                    color_select,
                    ft.Row(
                        [
                            ft.ElevatedButton(text="Cancel", on_click=lambda e: self.page.close(dialog)),
                            ft.ElevatedButton(text="Create", bgcolor=ft.Colors.BLUE_200, on_click=save_label),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

        self.page.open(dialog)

    def remove_label(self, label):
        self.labels = [lbl for lbl in self.labels if lbl != label]
        self.labels_view.controls = [self.create_label_view(lbl) for lbl in self.labels]
        self.store.update_item(self.list.board_list_id, self.item_id, self.item_text, self.labels)
        self.page.update()
        
    def delete_card(self, e):
        for control in self.list.items.controls:
            if isinstance(control, ft.Column):
                try:
                    control.controls.remove(self)
                    self.list.items.controls.remove(control) 
                    break
                except ValueError:
                    pass  
        self.store.remove_item(self.list.board_list_id, self.item_id) 
        self.list.update()