import builtins
from numbers import Number
from dataclasses import dataclass
import re
from rich.layout import Layout
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import InvalidResponse, PromptBase
from types import FunctionType
from typing import Any, Callable, Final, Literal, NamedTuple, NotRequired, TypedDict, Union, cast
from rich.live import Live
from rich.console import Console
from rich.text import Text
from datetime import date, datetime, time
from time import sleep


type AnswerDtype = Literal["str","int","float","bool","date","datetime","time"]

console = Console(color_system="truecolor")
err_console = Console(color_system="truecolor", stderr=True, style="bold on #E50202")

live_settings = {
        "console": console,
        "auto_refresh": False,
        "transient": True
        }

class LiveSettings(NamedTuple):
    console: Console = console
    auto_refresh: bool = False
    transient: bool = True


class Question(TypedDict):
    name: str
    question: str|Text
    ret_type: AnswerDtype
    when: NotRequired[FunctionType]
    validator: NotRequired[Callable[[Any], tuple[bool, Text|None]]]



class QuestionSequence(TypedDict):
    questions: tuple[Question,...]
    answers: dict[str,Any]


def get_valid_answer(question: Question, live: Live, err_msg: Text|None):
    assert "validator" in question
    while True:
        if err_msg:
            live.console.print(err_msg)
        live.refresh()
        answer = console.input()
        valid, err_msg = question["validator"](answer)
        if valid:
            return answer
        continue


US_DATE_FORMAT: Final[dict] = {"formats": ("%m/%d/%y","%m/%d/%Y"),
                  "regex": re.compile(r'^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/(\d{2}|\d{4})$')
                  }
@dataclass
class DatetimeFormats:
    """
    dates: 
    US, EU and ISO standard date formats 
    2DY = 'two digit year e.g 26'
    4DY = 'four digit year e.g 2026'
    """
    US_DATE_FORMAT = {"formats": ("%m/%d/%y","%m/%d/%Y"),
                      "regex": re.compile(r'^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/(\d{2}|\d{4})$')
                      }

    US_DATETIME_FORMAT_2DY = "%m/%d/%y %I:%M %p"
    US_MIL_DATETIME_FORMAT_2DY = "%m/%d/%y H:M" 
    US_DATETIME_FORMAT_4DY = "%m/%d/%Y %I:%M %p"
    US_MIL_DATETIME_FORMAT_4DY = "%m/%d/%Y H:M"
    EU_DATE_FORMAT_2DY = "%d/%m/%Y"
    EU_DATE_FORMAT_4DY = "%d/%m/%y"
    ISO_STANDARD_DATE_FORMAT_4DY = "%Y/%m/%d"
    ISO_STANDARD_DATE_FORMAT_2DY = "%y/%m/%d"
    TWELVE_HR_TIME_FORMAT = "%I:%M %p"
    MILITARY_TIME_FORMAT = "%H:%M"



    def __post__init__(self):
        print(self.US_DATE_FORMAT["regex"])




class StrPrompt(PromptBase[str]):
    response_type = str
    err_msg = "[promt.invalid]Error: %"


    
    def process_response(self, value: str) -> str:
        return value






class DatePrompt(PromptBase[datetime|date]):
    response_type = datetime
    date_regex: Final[re.Pattern] = re.compile(r"^(0[1-9]|1[0-2])\/(0[1-9]|[12][0-9]|3[01])\/(19|20)\d{2}$")
    datetime_regex: Final[re.Pattern] = re.compile("")


    def process_response(self, value: str) -> date|datetime:
        if value == "now":
            now = datetime.now().strftime("format")
            return datetime.strptime(now,"")
        elif self.date_regex.fullmatch(value):
            return datetime.strptime(value, "").date()
        elif self.datetime_regex.fullmatch(value):
            return datetime.strptime(value,"")
        else:
            return datetime(1,1,1)


class NumericPrompt(PromptBase[int|float]):
    err_msgs = {"out of range": "{} is out of the required range ({} - {})",
                "not a number": "{} is not a number !"}
    response_type = Number
    min =None
    max =None


    @classmethod
    def ask(cls,*args,min=None,max=None, **kwargs):
        if min is not None and max is not None and min == max:
            raise ValueError("max and min cannot be the same value")
        if (min is not None and not isinstance(min,int|float) or 
            max is not None and not isinstance(max,int|float)):
            raise TypeError("min and max must be integers, floats or None, None is the default !")
        cls.min = min
        cls.max = max
        return super().ask(*args, **kwargs)


    def check_range(self,number: int|float):
        if self.min is not None and number < self.min:
            return False

        if self.max is not None and number > self.max:
            return False

        return True



    def process_response(self, value: str) -> int|float:
        if not value.isdigit() and '.' in value:
            try:
                float(value)
            except Exception:
                raise InvalidResponse(self.err_msgs["not a number"].format(value))
            else:
                number = float(value)
        elif value.isdigit() or value.removeprefix("-").isdigit():
            number = int(value)
        else:
            raise InvalidResponse(self.err_msgs["not a number"].format(value))
        if self.check_range(number):
            console.print(self.min, self.max)
            return number
        else:
            raise InvalidResponse(
                    self.err_msgs["out of range"].format(
                        value,
                        self.min if self.min is not None else "-infinity",
                        self.max if self.max is not None else "infinity"))



            








def str_to_text(string: str, style: str|None=None, remove_nl: bool=True):
    if style is not None:
        return Text(string, style=style, end=" " if remove_nl else '\n')
    return Text(string,end=" " if remove_nl else '\n')


def _ask_live_sequence(settings: LiveSettings, questions: QuestionSequence):
    questions["answers"] = {}
    question_log = Text(end="") 
    # turn each str to rich Text object

    initial_question = questions["questions"][0]
    initial_question_str = str_to_text(questions["questions"][0]["question"]) # pyright: ignore[]

    with Live(initial_question_str, **settings._asdict()) as live:
        answer = console.input()
        if "validator" in initial_question:
            valid = initial_question["validator"](answer)

            if not valid[0]:
                answer = get_valid_answer(initial_question, live,valid[1] if valid[1] else None)

        question_log.append_text(initial_question_str.append_text(Text(" " + answer + "\n",style="bold #00DB1F")))
        live.console.clear()
        live.refresh()

        for question in questions["questions"][1:]:
            assert isinstance(question["question"],str)
            live.console.clear()
            question = str_to_text(question["question"])
            live.update(question_log.append_text(question), refresh=True)
            answer = console.input()
            question_log.append_text(Text(" " + answer + "\n", style="bold #00DB1F"))
            live.update(question_log, refresh=True)

        live.console.clear()
        console.print(question_log)





        ...

def ask_user(question: Question|QuestionSequence,
             settings: LiveSettings=LiveSettings()):
    if "answers" not in question: 
        assert "question" in question and "ret_type" in question
    else: 
        answer = _ask_live_sequence(settings, question)

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


            


def main():

    # a = NumericPrompt()
    # a.ask("", min=0)
    # ask_user(QS, LiveSettings())
    ...


if __name__ == "__main__":
    main()
