from abc import abstractmethod
import builtins
from dataclasses import dataclass, fields
from numbers import Number
from pickle import BUILD
import sys
from types import FunctionType, LambdaType
from color_palette import ClrPal
from datetime import datetime, date, time, timedelta 
from typing import Any, Callable, Final, Literal, NamedTuple, NewType, Optional, TextIO, TypedDict, overload
from rich.live import Live
from rich.text import Text
from rich.console import Console


_console = Console(color_system="truecolor")



type Result = str
type PromptStyle = Literal["custom_inline", "important","criticaly_important","default"]
type ValidCalendarUnits = Literal["year", "years", "month", "months", "week", "weeks", "day", "days"]
type ValidTimeUnits = Literal["hour", "hours", "minute", "minutes", "seconds", "seconds", "microsecond", "microseconds"]
type TimeData = tuple[int|float, ValidCalendarUnits|ValidTimeUnits]


VALID_CALENDAR_UNITS = {
        "year": frozenset({"yrs","yr", "years"}),
        "month": frozenset({"mth","mths","months"}),
        "week": frozenset({"wk","wks","weeks"}),
        "day": frozenset({"days", "dy", "dys"}),
                        }
REV_VALID_CALENDAR_UNITS = {}

VALID_TIME_UNITS = {
        "hour": frozenset({"hr", "hrs", "hours"}),
        "minute": frozenset({"min", "mins", "minutes"}),
        "second": frozenset({"sec", "secs", "seconds"}),
        "microsecond": frozenset({"mu", "msec", "microseconds"}),
        }
REV_VALID_TIME_UNITS = {}

def create_reverse_dict(original: dict, *,reverse: dict):
    for k,v in original.items():
        if k in reverse or v in reverse:
            raise ValueError("Duplicate found during reverse dict opp")
        reverse[v] = k

create_reverse_dict(VALID_TIME_UNITS,reverse=REV_VALID_TIME_UNITS)
create_reverse_dict(VALID_CALENDAR_UNITS,reverse=REV_VALID_CALENDAR_UNITS)

# _console.print(f"[bold {ClrPal.RED}]FORWARD DICT[/]{VALID_TIME_UNITS},\n\n[bold {ClrPal.RED}]REVERSE DICT[/]{REV_VALID_TIME_UNITS}")
# _console.print(f"[bold {ClrPal.RED}]FORWARD DICT[/]{VALID_CALENDAR_UNITS},\n\n[bold {ClrPal.RED}]REVERSE DICT[/]{REV_VALID_CALENDAR_UNITS}")

frozenset({"years", "yrs", "yr", "months","mth", "mths", "weeks","wk","wks",
                  "days","day", "hours","hrs","hr", "minutes", "min", "mins", "seconds",
                  "sec","secs", "microseconds", "ms"})

TRUTHY_RESPONSES = frozenset({"yes","y","yea","sure","yeah","fuck yeah", "hell yeah"})
FALSEY_RESPONSES = frozenset({"no","n","nah","im good","nay","fuck no", "hell no"})

_PromptStyleMap: dict[PromptStyle, str] = {
        "important": f"bold {ClrPal.ORG}",
        "criticaly_important": f"bold {ClrPal.RED} underline",
        "default": "bold"}

HINT_STYLE: Final[str] = "[bold #EB05BD]"
CRIT_ERR_STYLE: Final[str] = "[bold #EB2005 underline]"
WARN_ERR_STYLE: Final[str] = "[bold #FF7A00]"
MINOR_ERR_STYLE: Final[str] = "[#FFF700]"
SUCCESS_STYLE: Final[str] = "[#9FF500]"
ISO_DATE_FMT: Final[str] = "%Y/%m/%d"
ISO_DATETIME_FMT: Final[str] = "%Y/%m/%d %H:%M:%S.%f"
DATE_FMT: Final[str] = "%m/%d/%y"
DATETIME_FMT: Final[str] = "%m/%d/%y %I:%M %p"
TIME_FMT: Final[str] = "%I:%M %p"
ISO_TIME_FMT: Final[str] = "%H:%M:%S.%f"



@dataclass(slots=False,frozen=True)
class ErrorMsgs:
    """
    ErrMsg: tuple[str,str] 
    index 0 is the error msg itself and index 1 is the style 
    """
    invalid_dtype: str=f"{CRIT_ERR_STYLE}ERROR[/]: {WARN_ERR_STYLE}{{}}[/] {CRIT_ERR_STYLE}is not a valid datatype !"
    invalid_format: str=f"""{CRIT_ERR_STYLE}ERROR[/]: {WARN_ERR_STYLE}{{}}[/] {CRIT_ERR_STYLE}is not a valid format!
Format must be {{}}"""
    invalid_choice: str=f"{MINOR_ERR_STYLE}{{}}[/] {CRIT_ERR_STYLE}is an invalid choice !"
    min_range_failure: str =f"{MINOR_ERR_STYLE}{{}}[/] [bold]is too small answer must be >={{}}"
    max_range_failure: str =f"{MINOR_ERR_STYLE}{{}}[/] [bold]is too large answer must be <={{}}"
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

def str_to_time(time_str: str, as_iso: bool=False) -> None|time:
    try:
        if not as_iso:
            time_obj = datetime.strptime(time_str, TIME_FMT).time()
        else:
            time_obj = datetime.strptime(time_str, ISO_TIME_FMT).time()
    except Exception:
        return 
    return time_obj

def get_timedelta(x: date|datetime, y: date|datetime) -> timedelta:
    ...

def check_skippability(skippable: bool, skip_err_msg: str):
    if skippable:
        return PromptResult(True, "", None)
    return PromptResult(False, "", skip_err_msg)

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
@overload
def prompt_numeric(prompt: str,
                   style: PromptStyle="default",
                   ret_type: type[int]=int,
                   validation: Callable[[str], tuple[str,bool]]|None=None ,
                   skippable: bool=False,
                   min: int|float|None=None,
                   max: int|float|None=None,
                   show_range: bool=True,
                   error_msgs: ErrorMsgs=ErrorMsgs()
                   ) -> int|PromptResult: ...

@overload
def prompt_numeric(prompt: str,
                   style: PromptStyle="default",
                   ret_type: type[float]=float,
                   validation: Callable[[str], tuple[str,bool]]|None=None ,
                   skippable: bool=False,
                   min: int|float|None=None,
                   max: int|float|None=None,
                   show_range: bool=True,
                   error_msgs: ErrorMsgs=ErrorMsgs()
                   ) -> float|PromptResult: ...

def prompt_numeric(prompt: str,
                   style: PromptStyle="default",
                   ret_type: type[int|float]=int,
                   validation: Callable[[str], tuple[str,bool]]|None=None ,
                   skippable: bool=False,
                   min: int|float|None=None,
                   max: int|float|None=None,
                   show_range: bool=True,
                   error_msgs: ErrorMsgs=ErrorMsgs()
                   ) -> int|float|PromptResult:
    
    if min is not None and max is not None:
        assert min != max
    if style != "custom_inline":
        prompt = style + prompt 
    if show_range:
        prompt = prompt + f" ({min if min is not None else "   "} - {max if max is not None else "   "}): "
    else:
        prompt = prompt + ": "

    answer = _console.input(prompt)
    if (empty_answer := answer.strip() == "") and not skippable:
        return PromptResult(False,answer,error_msgs.not_skippable)
    elif empty_answer and skippable:
        return PromptResult(True,"",None)
    try:
        numeric_answer = ret_type(answer)
    except Exception:
        return PromptResult(False,answer,error_msgs.invalid_dtype.format(answer))
    if min is not None and not (numeric_answer >= min):
        return PromptResult(False,numeric_answer,error_msgs.min_range_failure.format(answer,min))
    if max is not None and not (numeric_answer <= max):
        return PromptResult(False,answer,error_msgs.max_range_failure.format(answer,max))
    if validation is not None:
        valid = validation(answer)
        if not valid:
            return PromptResult(False,answer,error_msgs.validation_error)
    return numeric_answer
  
        


# prompts for yes or no and true or false
def prompt_confirm(prompt: str,
                   style: PromptStyle="default",
                   skippable: bool=False,
                   error_msgs: ErrorMsgs=ErrorMsgs()
                   ) -> bool|PromptResult:
    if style != "custom_inline":
        prompt = _PromptStyleMap[style] + prompt + ": "
    answer = _console.input(prompt)
    if (empty_answer := answer.strip() == "") and not skippable:
        return PromptResult(False,answer,error_msgs.not_skippable)
    elif empty_answer and skippable:
        return PromptResult(True,"",None)
    answer = answer.strip().lower()
    if answer in TRUTHY_RESPONSES:
        return  True
    elif answer in FALSEY_RESPONSES:
        return False
    return PromptResult(False,answer, error_msgs.invalid_dtype.format(answer))


def deduce_timedelta(answer: str):
    answer_arr = answer.split()
    answer_parts = len(answer_arr)
    if (answer_parts % 2) != 0 or answer_parts < 2:
        # time can only be given in pairs of 2 i.e: 2 weeks, 3 days, 4 hours 
        return 
    if len(answer_arr) == 2:
        time_amnt, time_unit = answer_arr
    elif len(answer_arr):
        ...
    
    ...


def is_leap_year():
    curr_year = datetime.today().year
    return (curr_year % 4 == 0 and curr_year % 100 != 0) or curr_year % 400 == 0

def is_int(x: str) -> bool:
    try:
        int(x)
    except Exception:
        return False
    return True


def is_float(x: str) -> bool:
    try:
        float(x)
    except Exception:
        return False
    return True

def is_cal_or_time_unit(x: str):
    if (VALID_TIME_UNITS.get(x) is None and REV_VALID_TIME_UNITS.get(x) is None):
        return False
    

def deduce_elapsed_time(answer: str):
    split_units = answer.split()
    num_time_units = len(split_units)
    _console.print(split_units)
    if num_time_units < 2 or num_time_units % 2 != 0:
        return
    for num,unit in split_units:
        if not (num.isdigit() or is_float(num)) or not is_cal_or_time_unit(unit):
            return 
        else:
            return (num, unit)



    ...



# prompts for time of day or elapsed time in Years, Months, Days, Hours, Minutes, Seconds and Microseconds 
def prompt_time(prompt: str,
                style: PromptStyle="default",
                ret_type: Literal["time","timedelta","int","float","tuple[str,time]"]="time",
                as_iso: bool=False,
                forced_unit: ValidCalendarUnits|ValidTimeUnits|None=None,
                validation: Callable[[str], tuple[str,bool]]|None=None ,
                skippable: bool=False,
                error_msgs: ErrorMsgs=ErrorMsgs(),
                min: int|float|time|timedelta|None=None,
                max: int|float|time|timedelta|None=None,
                ) -> int|float|timedelta|time|tuple[str,time]|PromptResult:

    ret_type_obj: type|None = getattr(builtins, ret_type, None)
    if ret_type_obj is None:
        raise AttributeError("Must provide a valid return type !")

    """
    forced_unit: ValidCalendarUnits|ValidTimeUnits|None=None 
        Setting forced unit to one of the valid literals will restrict this 
        function to only return integers or floats. This is because you forced_unit 
        should only be used when you're asking the user a specific question that 
        pertains to the specified calendar or time unit.

        for example: How many hours will you work on this assignment ?: 
            forced_unit = hours
            function returns a int or float and the Question object 
            does the work of turning the number into the proper datatype 
    """

    if forced_unit is not None and not (ret_type_obj is float or ret_type_obj is int):
        raise TypeError("setting forced unit to any value other than None"
                        "requires that you set ret_type_obj to float or int only",
                        "see documentation for explanation")

    as_tuple = False
    if style != "custom_inline":
        prompt = _PromptStyleMap[style] + prompt + ": "
    answer = _console.input(prompt).strip()

    if answer == "":
        return check_skippability(skippable,
                                  error_msgs.not_skippable)

    #NOTE: move this into its own function called check_num_range() or some shit

    if ret_type_obj is int or ret_type_obj is float and forced_unit is not None:
        try:
            num_answer = ret_type_obj(answer)
        except Exception:
            return PromptResult(False,answer,error_msgs.invalid_dtype.format(answer))

        if min is not None and isinstance(min, float|int) and not (num_answer >= min):
            return PromptResult(False, num_answer, error_msgs.min_range_failure.format(answer, min))

        elif max is not None and isinstance(max, float|int) and not (num_answer <= max):
            return PromptResult(False, num_answer, error_msgs.max_range_failure.format(answer, max))

        elif not (isinstance(min, float|int) or isinstance(max,float|int)):
            raise ValueError("min and max args must be int or float valus when using forced_unit")
        return num_answer



    if ret_type_obj is time or (as_tuple := ret_type_obj == tuple[str,time]):
        if (time_answer := str_to_time(answer,as_iso)) is None:
            return PromptResult(False,answer, error_msgs.invalid_format.format(answer))
        return time_answer if not as_tuple else (answer, time_answer)


    # we want elapsed time back from this 
    if ret_type_obj == timedelta: 
        leap_year = is_leap_year()


        try:
            datetime.strptime(answer, TIME_FMT)
        except Exception:
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
    with Live(Text("", style="bold green"), console=_console, auto_refresh=False) as live:
        valid = False
        while not valid:
            validation = prompt_confirm(f"How many [bold {ClrPal.ORG}]BITCHES[/] you getting this year ?",
                                        style="custom_inline",
                                        skippable=True)
            if isinstance(validation, PromptResult):
                if validation.success and validation.answer == "":
                    _console.print(f"[{ClrPal.GRN}]SKIPPING ! :D")
                    live.refresh()
                    break
                    
                live.console.clear()
                _console.print(validation.err_msg)
                continue
            else:
                _console.print(validation)
                valid = True


if __name__ == "__main__":
    main()













