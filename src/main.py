from rich.console import Console
from click_options import ARG_OPTS as arg_opts 
from custom_types import ColorScheme
import click


console = Console(color_system="truecolor")


@click.command()
@click.argument("action")
@click.argument("target")
def goal_creation(action, target):
    key = f"{action}-{target}"
    if (operation := arg_opts.get(key)) is not None:
        operation()
    else:
        console.print(f"target: {target} or action: {action} are not valid !",style=ColorScheme.ERROR_2)
        ...
    ...


def get_version():
    console.print("speedyJ version: 0.0.1 - 1/8/26", style="#2AF500")


def main():
    ...

if __name__ == "__main__":
    goal_creation()
