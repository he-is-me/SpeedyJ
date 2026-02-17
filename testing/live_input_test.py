from rich.live import Live
from rich.columns import Columns
from rich.console import Console
from rich.text import Text
from time import sleep


console = Console(color_system="truecolor")

form = Text("""
name: 
age: 
height: 
""")





def main():
    with Live(form, console=console, auto_refresh=False) as live:
        ...


if __name__ == "__main__":
    main()
