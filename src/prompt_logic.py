import builtins
import re
from typing import Any, Literal, NamedTuple, TypedDict
from rich.live import Live
from rich.console import Console, RenderableType
from rich.text import Text
from datetime import date, datetime, time
from time import sleep



console = Console(color_system="truecolor")

live_settings = {
        "console": console,
        "auto_refresh": False,
        "transient": True
        }

class LiveSettings(NamedTuple):
    console: Console = console
    auto_refresh: bool = False
    transient: bool = True


class QuestionSequence():
    questions: dict[str|Text, tuple[str|None,
                          Literal["confirm", "numeric","date",
                                  "datetime", "time", "str"]]]
    answers: dict[str, Any]


time_delta_regex = {
        ""
        }

def question_live_ctx(settings: LiveSettings, questions: ):
    answers = {}
    with Live(renderable, **settings._asdict()) as live:
        sleep(4)
        ...
    ...


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


def datetime_prompt(question: Text,
                    time_type: Literal["date", "datetime", "time"],
                    min_val: date|datetime|time|None=None,
                    max_cal: date|datetime|time|None=None, 
                    ):
    question = question.append_text(Text(f"\n {time_type}: ", style="italic green"))
    with Live(question, **live_settings) as live:
        while True: 
            answer = console.input()

            
        ...
    ...

def multi_select_prompt():
    ...


def single_select_prompt():
    ...


def string_prompt():
    ...




def main():
    a = live_instance(LiveSettings(),Text("testing") )
    console.print(a)
    ...

if __name__ == "__main__":
    main()
