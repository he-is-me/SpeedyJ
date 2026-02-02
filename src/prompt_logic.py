import builtins
from typing import Literal
from rich.live import Live
from rich.console import Console
from rich.text import Text
from time import sleep


console = Console(color_system="truecolor")

live_settings = {
        "console": console,
        "auto_refresh": False,
        "transient": True
        }

def confirm_prompt(question: Text, confirm_type: Literal["yes or no", "true or false"]="yes or no") -> bool:
    f_question = question.copy()
    if confirm_type == "yes or no":
        f_question = f_question.append_text(Text("  \t[(y)es or (n)o]", style="bold #F500A4"))
        question = question.append_text(Text("  \t[(y)es or (n)o]\n", style="bold #F500A4"))
    else:
        f_question = f_question.append_text(Text("  \t[(t)rue or (f)alse]", style="bold #F500A4"))
        question = question.append_text(Text("  \t[(t)rue or (f)alse]\n", style="bold #F500A4"))

    with Live(question,**live_settings) as live:
        while True:
            answer = console.input()
            if answer.lower() in ["yes", "y", "true", "t"]:
                answer = True
                break
            elif answer.lower() in ["no", "n", "false", "f"]:
                answer = False
                break
            else:
                live.console.clear()
                live.console.print(Text(f"Invalid answer '{answer}'!", style="bold #F55900 underline"))
                live.refresh()
                continue
        live.console.clear()
    console.print(f_question.append_text(Text(f": {answer}" ,style="bold green")))
    return answer


def number_prompt(question: Text, min_val: int, max_val: int, numeric_type: Literal["float","int"]="float"):
    number = getattr(builtins,numeric_type)
    question = question.append_text(Text(f"\t[{min_val} - {max_val}]\n", style="bold #F500A4"))
    with Live(question, **live_settings) as live:
        while True: 
            answer = console.input()
            if answer.isdigit() and number(answer) >= min_val and number(answer) <= max_val:
                return number(answer)
            else:
                live.console.clear()
                live.console.print(Text(f"Invalid answer '{answer}' numbers {min_val} to {max_val} only",
                                        style="bold red underline")) 
                live.refresh()
                continue



def datetime_prompt():
    ...

def multi_select_prompt():
    ...


def single_select_prompt():
    ...


def string_prompt():
    ...




def main():
    a = confirm_prompt(Text("this is a question !!", style="bold red"))
    a = confirm_prompt(Text("this is a question !!", style="bold red"))
    console.print(a)
    ...

if __name__ == "__main__":
    main()
