from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Input, ProgressBar, Header, Button
from textual.containers import Horizontal, VerticalScroll, Center

import yaml
import dotenv
import argparse

class EnvVarTracker():
    def __init__(self):
        self.current_vars = {}
    
    def update_vars(self, vars: list[tuple]):
        for var in vars:
            key, value = var
            self.current_vars[key] = value

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
        env_file_name = app.env_file

        # Handle going forward
        if event.button.id == "exitBtn":
            env_vars_tracker: EnvVarTracker = app.env_vars_tracker
            for k, v in env_vars_tracker.current_vars.items():
                dotenv.set_key(env_file_name, k, v)
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
        self.screen_var_elements = []

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
            input_label = Label(var.get('name'), name=var.get('name'), classes="inputLabel")

            input_area = None
            if var.get('sensitive'):
                input_area = Input(placeholder=var.get('placeholder'), classes="inputArea", password=True)
            else:
                input_area = Input(placeholder=var.get('placeholder'), classes="inputArea")

            # Add to container widgets
            container_widgets.append(input_label)
            container_widgets.append(input_area)

            # Add to screens var list
            self.screen_var_elements.append({"LabelElement": input_label, "InputElement": input_area})
    
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
            for elem in self.screen_var_elements:
                label_elem = elem['LabelElement']
                input_elem = elem['InputElement']

                env_vars_tracker: EnvVarTracker = self.app.env_vars_tracker
                env_vars_tracker.update_vars([(label_elem.name, input_elem.value)])

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
    def __init__(self, variable_groups: list, env_file: str):
        super().__init__()
        self.variable_groups = variable_groups
        self.progress_total = len(variable_groups)
        self.env_vars_tracker = EnvVarTracker()
        self.env_file = env_file

    def on_mount(self) -> None:
        self.push_screen(SecureMeScreen(self.variable_groups,
                                        0,
                                        self.progress_total))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="SecureMe",
                                     description="A Simple TUI application for setting ENV vars")

    parser.add_argument("metadata_file", help="YAML Metadata file describing variables to set.")
    parser.add_argument("env_file", help="Environment file to set ENV vars in.")

    args = parser.parse_args()

    metadata_file = args.metadata_file
    env_file = args.env_file

    variable_groups = None
    with open(metadata_file, "r") as f:
        variable_groups = yaml.safe_load(f)
    app = SecureMeApp(variable_groups=variable_groups,
                      env_file=env_file)
    app.run()