import questionary
from questions import QUESTIONS
from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt

console = Console(color_system="truecolor")




def create_new_goal():
    questionary.prompt(QUESTIONS["new_goal"])
    ...

def create_new_task():
    ...

def create_new_habit():
    ...






def setup_new_goal_layout():
    console.print(Panel("Welcome to Tiny J !", title_align="center"))
    ...




def main():
    create_new_goal()

if __name__ == "__main__":
    main()
