from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Input, ProgressBar, Header, Button
from textual.containers import Horizontal, VerticalScroll, Center
from textual.validation import Length, ValidationResult, Regex

from schema import Schema, And, Optional

from typing import List, Tuple
import yaml
import dotenv
import argparse

METADATA_SCHEMA = Schema(
    [
        And(
            {
                "var_group": {
                    "title": str,
                    "vars": [
                        {
                            "var": {
                                "name": str,
                                "placeholder": str,
                                Optional("sensitive"): bool,
                                Optional("complexity"): {
                                    Optional("max_length"): int,
                                    Optional("min_length"): int,
                                    Optional("numbers"): int,
                                    Optional("symbols"): int,
                                    Optional("uppercase"): int
                                }
                            }
                        }
                    ]
                }
            }
        )
    ]
)


def metadata_verification(yaml_data: List[dict]) -> bool:
    """Verifies the YAML data is properly formatted"""
    return METADATA_SCHEMA.is_valid(yaml_data)


class EnvVarTracker():
    def __init__(self):
        self.current_vars = {}

    def update_vars(self, vars: List[Tuple]):
        for var in vars:
            key, value = var
            self.current_vars[key] = value


class DoneScreen(Screen):

    CSS_PATH = "./tcss/exit_screen.tcss"

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


class SecureEnvScreen(Screen):

    CSS_PATH = "./tcss/main_screen.tcss"

    def __init__(self,
                 variable_groups: List,
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
            input_label = Label(var.get('name'), name=var.get('name'),
                                classes="inputLabel")

            input_area = None

            max_length = 25
            min_length = 5
            numbers = 0
            symbols = 0
            uppercase = 0
            complexity = var.get('complexity')
            if complexity:
                max_length = complexity.get('max_length', max_length)
                min_length = complexity.get('min_length', min_length)
                numbers = complexity.get('numbers', numbers)
                symbols = complexity.get('symbols', symbols)
                uppercase = complexity.get('uppercase', uppercase)

            if var.get('sensitive'):
                input_area = Input(placeholder=var.get('placeholder'),
                                   classes="inputArea",
                                   password=True,
                                   max_length=max_length,
                                   valid_empty=False,
                                   validators=[
                                        Length(min_length, max_length,
                                               failure_description=f"{var.get('name')} must be between {min_length} and {max_length}"),
                                        Regex(regex=("^(?:[^0-9]*[0-9]){%d}.*" % (numbers)),
                                              failure_description=f"{var.get('name')} must have at least {numbers} numbers in it"),
                                        Regex(regex=("^(?:[^!@#$]*[!@#$]){%d}.*" % (symbols)),
                                              failure_description=f"{var.get('name')} must have at least {symbols} symbols in it"),
                                        Regex(regex=("^(?:[^A-Z]*[A-Z]){%d}.*" % (uppercase)),
                                              failure_description=f"{var.get('name')} must have at least {symbols} uppercase letters in it")
                                   ])
            else:
                input_area = Input(placeholder=var.get('placeholder'),
                                   classes="inputArea",
                                   max_length=max_length,
                                   valid_empty=False,
                                   validators=[
                                       Length(min_length, max_length,
                                              failure_description=f"{var.get('name')} must be between {min_length} and {max_length}"),
                                       Regex(regex=("^(?:[^0-9]*[0-9]){%d}.*" % (numbers)),
                                             failure_description=f"{var.get('name')} must have at least {numbers} numbers in it"),
                                       Regex(regex=("^(?:[^!@#$]*[!@#$]){%d}.*" % (symbols)),
                                             failure_description=f"{var.get('name')} must have at least {symbols} symbols in it"),
                                       Regex(regex=("^(?:[^A-Z]*[A-Z]){%d}.*" % (uppercase)),
                                             failure_description=f"{var.get('name')} must have at least {uppercase} uppercase letters in it")
                                   ])

            # Add to container widgets
            container_widgets.append(input_label)
            container_widgets.append(input_area)

            # Add to screens var List
            self.screen_var_elements.append({"LabelElement": input_label,
                                             "InputElement": input_area})

        next_button = Button("Next", id="nextBtn")

        btn_container = None
        if self.nth > 0:  # Don't show previous button on first input
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
        invalid_form = False
        if event.button.id == "nextBtn":
            for elem in self.screen_var_elements:
                label_elem = elem['LabelElement']
                input_elem: Input = elem['InputElement']

                validation_result: ValidationResult = input_elem.validate(
                    input_elem.value
                )

                if len(validation_result.failures) > 0:
                    invalid_form = True
                    msg = validation_result.failures[0].validator.failure_description
                    self.notify(msg, severity="error", timeout=3)
                    break

                env_vars_tracker: EnvVarTracker = self.app.env_vars_tracker
                env_vars_tracker.update_vars([(label_elem.name,
                                               input_elem.value)])

            if not invalid_form:
                # Check if done
                if ((self.nth+1) == len(self.variable_groups)):
                    app.push_screen(DoneScreen())

                else:
                    app.push_screen(SecureEnvScreen(self.variable_groups,
                                                    self.nth + 1,
                                                    self.progress_total))
        # Handle going back in stack
        if event.button.id == "prevBtn":
            app.pop_screen()


class SecureEnvApp(App):
    def __init__(self, variable_groups: List, env_file: str):
        super().__init__()
        self.variable_groups = variable_groups
        self.progress_total = len(variable_groups)
        self.env_vars_tracker = EnvVarTracker()
        self.env_file = env_file

    def on_mount(self) -> None:
        self.push_screen(SecureEnvScreen(self.variable_groups,
                                         0,
                                         self.progress_total))


def main():
    parser = argparse.ArgumentParser(
        prog="securenv",
        description="Simple TUI for Defining and Constraining Environment Variables"
    )

    parser.add_argument("metadata_file",
                        help="YAML Metadata file describing variables to set.")
    parser.add_argument("env_file",
                        help="Environment file to set ENV vars in.")

    args = parser.parse_args()

    metadata_file = args.metadata_file
    env_file = args.env_file

    variable_groups = None
    try:
        with open(metadata_file, "r") as f:
            variable_groups = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Unable to find file: {metadata_file}")
        exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occured: {e}")
        exit(1)

    if variable_groups is None:  # Extra sanity check
        print("Error: No metadata loaded. Ensure the YAML file is properly formatted.")
        exit(1)

    if not metadata_verification(variable_groups):
        print("Error: Metadata format is invalid. Please refer to documentation on properly structuring the metadata file.")
        exit(1)

    app = SecureEnvApp(variable_groups=variable_groups,
                       env_file=env_file)
    app.run()


if __name__ == "__main__":
    main()
