from abc import abstractmethod
from dataclasses import dataclass, fields
from types import FunctionType, LambdaType
from datetime import datetime, date, time 
from typing import Any, Callable, Final, Literal, NamedTuple, NewType, Optional, TextIO, TypedDict
from rich.live import Live
from rich.text import Text
from rich.console import Console


type Result = str

HINT_STYLE: Final[str] = "[bold #EB05BD]"
CRIT_ERR_STYLE: Final[str] = "[bold #EB2005 underline]"
WARN_ERR_STYLE: Final[str] = "[bold #FF7A00]"
MINOR_ERR_STYLE: Final[str] = "[#FFF700]"
SUCCESS_STYLE: Final[str] = "[#9FF500]"
ISO_DATE_FMT: Final[str] = "%Y/%m/%d"
ISO_DATETIME_FMT: Final[str] = "%Y/%m/%d %H:%M:%S.%f"
DATE_FMT: Final[str] = "%m/%d/%y"
DATETIME_FMT: Final[str] = "%m/%d/%y %I:%M %p"


_console = Console(color_system="truecolor")

@dataclass(slots=False,frozen=True)
class ErrorMsgs:
    """
    ErrMsg: tuple[str,str] 
    index 0 is the error msg itself and index 1 is the style 
    """
    invalid_dtype: str=f"{CRIT_ERR_STYLE}ERROR[/]: {WARN_ERR_STYLE}{{}}[/] {CRIT_ERR_STYLE}is not a valid datatype !"
    invalid_format: str=f"""{CRIT_ERR_STYLE}ERROR[/]: {WARN_ERR_STYLE}{{}}[/] {CRIT_ERR_STYLE}is not a valid format!
Format must be {{}}"""
    invalid_choice: str=f"{MINOR_ERR_STYLE} {{}}[/] {CRIT_ERR_STYLE}is an invalid choice !"
    not_skippable: str=f"{MINOR_ERR_STYLE}This question in NOT skippable !"
    validation_error: str=f"{WARN_ERR_STYLE}{{}}[/] {CRIT_ERR_STYLE}is an invalid answer !"


    def __post__init__(self):
        for field in fields(self):
            assert isinstance(field, str)
            field = Text(field)



class PromptResult(NamedTuple):
    success: bool
    answer: Any
    err_msg: Text|str|None


class Question(NamedTuple):
    question: str
    exp_ret_type: type|Literal["print"] # the type determines which prompter is used, None means its just for printing
    validation: Callable[[str], bool]|None=None 
    post_answer_logic: Callable[[Any], Any]|None=None # if you want to do something with the answer like a calculation or change it
    skippable: bool=False
    skip_if: LambdaType|Callable[[Any], bool]|None=None # skip this question if this is true
    followup_if: tuple[Callable[[Any], bool], "Question"]|None=None # ask an arbitrary followup question if this is True
    prefix_nl: int=0
    suffix_nl: int=0
    preffixed_str: str|None=None
    name: str="" # an alias for the question, if blank the question itself will be used as a key in answers dict


class QuestionSequence(NamedTuple):
    questions: tuple[Question,...]
    answers: dict[str,Any|None]

def str_to_date(date_str: str, ret_type: type[date|datetime], as_iso: bool=False) -> datetime|date|None:
    try:

        if ret_type == date:
            date_obj = datetime.strptime(date_str, DATE_FMT if not as_iso else ISO_DATE_FMT).date()
        else:
            date_obj = datetime.strptime(date_str, DATETIME_FMT if not as_iso else ISO_DATETIME_FMT)

    except Exception:
        return None 
    else:
        return date_obj 



#NOTE: fix error message...errors :D
# error message should not force formatting, or maybe they should ? 
def prompt_date(prompt: str|Text,
                style: str="bold",
                ret_type: type[date|datetime]=date,
                as_iso: bool=False,
                validation: Callable[[str], tuple[str,bool]]|None=None ,
                skippable: bool=False,
                insert_nl: int=0,
                error_msgs: ErrorMsgs=ErrorMsgs()
                ) -> date|datetime|PromptResult:

    prefixed_suggestion = Text(" (MM/DD/YY): " if ret_type == date else " (MM/DD/YY HH:MM am/pm): "
                               , style=HINT_STYLE.removeprefix("[").removesuffix("]"))
    if isinstance(prompt,str):
        prompt = Text(prompt, style=style).append_text(prefixed_suggestion)
    else:
        prompt = prompt.append_text(prefixed_suggestion)
    answer = _console.input(prompt)

    if answer == "now":
        today = datetime.today().strftime(DATETIME_FMT)
        return datetime.strptime(today,DATETIME_FMT)
    elif (empty_answer :=answer.strip() == "") and not skippable:
        return PromptResult(False,answer,error_msgs.not_skippable)

    elif empty_answer and skippable:
        return PromptResult(True, "",None)

    if (date_answer := str_to_date(answer,ret_type, as_iso)) is None:
        return PromptResult(False,answer,error_msgs.invalid_format.format(answer,
                                                                          "MM/DD/YY" if ret_type == date else "MM/DD/YY HH:MM am/pm"))
    else:
        if validation is not None:
            valid = validation(answer)
            if valid:
                return date_answer
            else:
                return PromptResult(False,answer,error_msgs.validation_error.format(answer))
        return date_answer


# prompts for a integer, float or math equation i.e 180 + 20 will return 200
def prompt_numeric():
    ...

# prompts for yes or no and true or false
def prompt_confirm():
    ...

# prompts for time of day or elapsed time
def prompt_time():
    ...




def prompt_str(prompt: str,
               style: str="bold",
               validation: Callable[[str], tuple[str,bool]]|None=None ,
               skippable: bool=False,
               ) -> str|bool:

    answer = _console.input(Text(prompt + ": ", style=style))

    if (empty_answer:=answer.strip()) == "" and not skippable:
        return False
    elif empty_answer and skippable:
        return ""

    if validation is not None:
        answer, valid = validation(answer)
        if valid:
            return answer
        return False

    return answer


def main():
    with Live(Text("questions", style="bold green"), console=_console, auto_refresh=False) as live:
        valid = False
        while not valid:
            validation = prompt_date("What day were you born on ?", style="bold blue", ret_type=datetime)
            if isinstance(validation, PromptResult):
                live.console.clear()
                _console.print(validation.err_msg)
                continue
            else:
                _console.print(validation)
                valid = True


if __name__ == "__main__":
    main()













