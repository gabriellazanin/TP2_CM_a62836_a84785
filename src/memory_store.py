from typing import TYPE_CHECKING
import json
import os

if TYPE_CHECKING:
    from board import Board
    from board_list import BoardList
    from user import User
    from item import Item

from data_store import DataStore

STORAGE_FILE = "storage.json"

class InMemoryStore(DataStore):
    def __init__(self):
        self.boards: dict[int, "Board"] = {}
        self.users: dict[str, "User"] = {}
        self.board_lists: dict[int, list["BoardList"]] = {}
        self.items: dict[int, list["Item"]] = {}
        
        self.load_data() #carregar o arquivo JSON

    def load_data(self):
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            for list_data in data ["lists"]:
                self.board_lists[list_data["id"]] = []
            for card_data in data["cards"]:
                list_id = card_data["list_id"]
                if list_id not in self.items:
                    self.items[list_id] = []
                self.items[list_id].append(card_data)
                
    # def save_data(self):
    #     data = {
    #         "lists": [{"id": k, "title": v[0].title, "color": v[0].color} for k, v in self.board_lists.items() if v],
    #         "cards": [card for sublist in self.items.values() for card in sublist]
    #     }
    #     with open(STORAGE_FILE, "w", encoding="utf-8") as file:
    #         json.dump(data, file, indent=4)
    

    def add_board(self, board: "Board"):
        self.boards[board.board_id] = board

    def get_board(self, id: int):
        return self.boards[id]

    def update_board(self, board: "Board", update: dict):
        for k in update:
            setattr(board, k, update[k])

    def get_boards(self):
        return [self.boards[b] for b in self.boards]

    def remove_board(self, board: "Board"):
        del self.boards[board.board_id]
        self.board_lists[board.board_id] = []

    def add_list(self, board: int, list: "BoardList"):
        if board in self.board_lists:
            self.board_lists[board].append(list)
        else:
            self.board_lists[board] = [list]
        # self.save_data()

    def get_lists_by_board(self, board: int):
        return self.board_lists.get(board, [])

    def remove_list(self, board: int, id: int):
        self.board_lists[board] = [
            l for l in self.board_lists[board] if not l.board_list_id == id
        ]
        self.save_data()

    def add_user(self, user: "User"):
        self.users[user.name] = user

    def get_users(self):
        return [self.users[u] for u in self.users]

    def add_item(self, board_list: int, item: "Item"):
        if board_list in self.items:
            self.items[board_list].append(item)
        else:
            self.items[board_list] = [item]
        # self.save_data()    

    def get_items(self, board_list: int):

        return [
            {"id": item.item_id, "text": item.item_text, "list_id": board_list}
            for item in self.items.get(board_list, [])
        ]

    def remove_item(self, board_list: int, id: int):
        self.items[board_list] = [
            i for i in self.items[board_list] if not i.item_id == id
        ]
        # self.save_data()
    
    def update_item(self, board_list, item_id, new_text):
        if board_list in self.items: 
            for item in self.items.get(board_list,[]):
                if item.item_id == item_id:
                    item.item_text = new_text
                    break
        # self.save_data()