from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Input, ProgressBar, Header, Button
from textual.containers import Horizontal, VerticalScroll, Center

import os

import yaml

class DoneScreen(Screen):

    CSS_PATH = "exit_screen.tcss"

    def compose(self) -> ComposeResult:
        yield Header()

        with Center():
            yield Label("All variables set! You can now exit the application.", id="exitLabel")
        with Center():
            yield Button("Exit", variant="primary", id="exitBtn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:  
        """Handle all button pressed events."""
        app = self.app

        # Handle going forward
        if event.button.id == "exitBtn":
            app.exit()

class SecureMeScreen(Screen):

    CSS_PATH = "main_screen.tcss"

    def __init__(self,
                 variable_groups: list,
                 nth: int,
                 progress_total: int):
        
        super().__init__()
        self.variable_groups = variable_groups
        self.nth = nth
        self.progress_total = progress_total

    def compose(self) -> ComposeResult:
        var_group = self.variable_groups[self.nth].get('var_group')

        title = var_group.get('title')
        yield Header()

        container_widgets = []

        header_label = Label("Variables Configured")
        container_widgets.append(header_label)
        progress_bar = ProgressBar(total=self.progress_total, show_eta=False)
        progress_bar.advance(self.nth)
        container_widgets.append(progress_bar)

        var_group_label = Label(title, classes="varGroupLabel")
        container_widgets.append(var_group_label)

        for var_def in var_group.get('vars'):
            var = var_def.get('var')
            container_widgets.append(Label(var.get('name'), classes="inputLabel"))

            if var.get('sensitive'):
                container_widgets.append(Input(placeholder=var.get('placeholder'), classes="inputArea", password=True))
            else:
                container_widgets.append(Input(placeholder=var.get('placeholder'), classes="inputArea"))
    
        next_button = Button("Next", id="nextBtn")

        btn_container = None
        if self.nth > 0: # Don't show previous button on first input
            back_button = Button("Previous", id="prevBtn")
            btn_container = Horizontal(
                back_button,
                next_button,
                id="btnContainer"
            )
        else:
            btn_container = Horizontal(
                next_button,
                id="btnContainer"
            )

        # Expand all into a vertical scroll
        yield VerticalScroll(
            VerticalScroll(
                *container_widgets,
                id="contentContainer"
            ),
            btn_container,
            id="bodyContainer"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:  
        """Handle all button pressed events."""
        app = self.app

        # Handle going forward
        if event.button.id == "nextBtn":
            # Check if done
            if ((self.nth+1) == len(self.variable_groups)):
                app.push_screen(DoneScreen())

            else:
                app.push_screen(SecureMeScreen(self.variable_groups,
                                            self.nth + 1,
                                            self.progress_total))
        # Handle going back in stack
        if event.button.id == "prevBtn":
            app.pop_screen()

class SecureMeApp(App):
    def __init__(self, variable_groups: list):
        super().__init__()
        self.variable_groups = variable_groups
        self.progress_total = len(variable_groups)

    def on_mount(self) -> None:
        self.push_screen(SecureMeScreen(self.variable_groups, 0, self.progress_total))

if __name__ == "__main__":
    variable_groups = None
    with open("metadata.yaml", "r") as f:
        variable_groups = yaml.safe_load(f)
    app = SecureMeApp(variable_groups=variable_groups)
    app.run()