import flet as ft
 
class TrelloApp:
    def __init__(self, page: ft.Page, user=None):
        self.page = page
        self.page.on_route_change = self.route_change
        self.appbar_items = [
            ft.PopupMenuItem(text="Login"),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="Settings")
        ]
        self.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=100,
            title=ft.Text("Trolli",size=32, text_align="start"),
            center_title=False,
            toolbar_height=75,
            bgcolor=ft.Colors.LIGHT_BLUE_ACCENT_700,
            actions=[
                ft.Container(
                    content=ft.PopupMenuButton(
                        items=self.appbar_items
                    ),
                    margin=ft.margin.only(left=50, right=25)
                )
            ],
        )
        self.page.appbar = self.appbar
        self.page.update()
        
    def initialize(self):
        self.page.views.append(
            ft.View(
                "/",
                [self.appbar, self],
                padding=ft.padding.all(0),
                bgcolor=ft.Colors.BLUE_GREY_200,
            )
        )
        self.page.update()
        # create an initial board for demonstration if no boards
        if len(self.boards) == 0:
            self.create_new_board("My First Board")
        self.page.go("/")

    def route_change(self, e):
        troute = ft.TemplateRoute(self.page.route)
        if troute.match("/"):
            self.page.go("/boards")
        elif troute.match("/board/:id"):
            if int(troute.id) > len(self.store.get_boards()):
                self.page.go("/")
                return
            self.set_board_view(int(troute.id))
        elif troute.match("/boards"):
            self.set_all_boards_view()
        elif troute.match("/members"):
            self.set_members_view()
        self.page.update()
if __name__ == "__main__":

    def main(page: ft.Page):

        page.title = "Flet Trello clone"
        page.padding = 0
        page.theme = ft.Theme(font_family="Verdana")
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme.page_transitions.windows = "cupertino"
        page.fonts = {"Pacifico": "/Pacifico-Regular.ttf"}
        page.bgcolor = ft.Colors.BLUE_GREY_200
        page.update()
        app = TrelloApp(page)

    ft.app(main, assets_dir="../assets")