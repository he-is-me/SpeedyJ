from types import FunctionType
from rich import print as rprint
from rich.prompt import Confirm, IntPrompt, PromptType, InvalidResponse, PromptBase
from typing import Any, Final, NamedTuple, Literal, NewType, Text, TypedDict, Callable
from enum import StrEnum
from datetime import date, datetime, time, timezone
from dataclasses import dataclass


type QuestionType = Literal["text", "confirm", "select", "print", "search"]
type AnswerType = type[str|bool|int|float|date|datetime|time|list[str]]
ConfidenceLevel = {"not confident", "kind of confident", "confident", "very confident", "extremely confident"}


class StrFormats(StrEnum):
    """
    dates: 
    US, EU and ISO standard date formats 
    2DY = 'two digit year e.g 26'
    4DY = 'four digit year e.g 2026'
    """
    US_DATE_FORMAT_2DY = "%m/%d/%y"
    US_DATE_FORMAT_4DY = "%m/%d/%Y"
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

class TimePrompt(PromptBase[date]):
    response_type = time 
    units = ["hour", "minute", "second", "milisecond"]  
    validate_error_message = "[prompt.invalid]Please enter a valid time HH:MM (am or pm) or HH:MM for military time."
    err_msg = {"non_digit": "[prompt.invalid]Non numerical character detected !",
               "format": "[prompt.invalid]Invalid time format ! (H*n:MM:SS.MS) only"}

    def validate_time_unit_2(self, value: str):
        for char in value:
            if char == ":" or char == ".":
                continue
            else:
                if not char.isdigit():
                    raise InvalidResponse(self.err_msg["non_digit"])
        unit = ""
        colon_count = value.count(":")
        period_count = value.count(".")
        if colon_count > 2 or period_count > 1:
            raise InvalidResponse(self.err_msg["format"])
        elif colon_count == 2:
            unit = "hours"
        elif colon_count == 1:
            unit = "minutes"
        elif colon_count == 0 and period_count == 1:
            period_index = value.index('.') - 1
            digits = value[:period_index]
            if all([(not bool(int(digit))) for digit in digits]):
                unit = "miliseconds"
            else:
                unit = "seconds"
        rprint(f"[bold red underline]{unit}")


    #
    # def validate_time_unit(self, value: str):
    #     unit = ""
    #     unit_idx = 0
    #     time_info = {}
    #     for idx, char in enumerate(value):
    #         if char.isdigit() or char == "." or char == ":" or char.isspace():
    #             continue
    #         elif char.isalpha() and idx > 0:
    #             unit = value[idx:]
    #             value = value.replace(unit,"").strip()
    #             if unit.endswith("s"):
    #                 unit = unit[0:-1]
    #             break
    #         else:
    #             raise InvalidResponse(f"Unsupported character: {char}")
    #     if unit not in self.valid_time_units:
    #         raise InvalidResponse(self.invalid_unit_err_msg)
    #     unit_idx = self.units.index(unit)
    #     time_intervals = value.split(":")
    #     if "." in time_intervals[-1]:
    #         time_intervals = time_intervals[0:-1] + time_intervals[-1].split(".")
    #     time_info["unit"] = unit 
    #     time_info["intervals"] = {}
    #     time_info["intervals"][unit] = time_intervals[0]
    #     time_info["time"] = value
    #     if unit != "milisecond":
    #         for idx,interval in enumerate(self.units[unit_idx + 1:], 1):
    #             if idx >= len(time_intervals):
    #                 break
    #             time_info["intervals"][interval] = time_intervals[idx]
    #     return time_info
    #

    def process_response(self, value: str, confirm_time: bool=True) -> time:
        rprint(self.validate_time_unit_2(value))




class DatePrompt(PromptBase[date]):
    response_type = datetime
    validate_error_message = "[prompt.invalid]Please enter a valid date MM/DD/YY or M/D/YY"

    def find_correct_format(self,value: str):
        for format in StrFormats:
            try:
                chosen_date = datetime.strptime(value, format.value)
            except ValueError:
                continue
            else:
                print(f"This is {format.name} format which is {format}")
                return format
        raise InvalidResponse("That format does not match one of the avalible ones !")




    def process_response(self, value: str) -> date:
        if value == "now":
            curr_utc_datetime= datetime.now(timezone.utc).astimezone()
            formatted_str = curr_utc_datetime.strftime(StrFormats.US_DATETIME_FORMAT_2DY)
            formatted_date = curr_utc_datetime.strptime(formatted_str, StrFormats.US_DATETIME_FORMAT_2DY)
            #NOTE ask user for prefered date format here then save to config !
            print(f"todays date is: {formatted_str}")
            return formatted_date
        elif value == "later":
            return datetime(1,1,1,1,1,1,1)
        try:
            chosen_date = datetime.strptime(value,StrFormats.US_DATE_FORMAT_2DY)
        except ValueError:
            format = self.find_correct_format(value)
            return datetime.strptime(value,format)
        else:
            return chosen_date



class IntegerPrompt(IntPrompt):
    def process_response(self, value: str): # pyright: ignore[]
        if value == "Q":
            return value
        return super().process_response(value)


class PromptValidator(TypedDict):
    func: Callable[[Any], bool]
    error_msg: str|Text
    loop_until_correct: bool


class Question(TypedDict, total=False):
    name: str
    type: QuestionType
    question: str|Text
    answer_type: AnswerType 
    when: FunctionType
    choices: list
    answer: Any
    kwargs: dict
    validator: PromptValidator
    callback: Callable

class ColorScheme(StrEnum):
    SUCCESS = "#51E000"
    ERROR = "#B00928"
    ERROR_2 = "#FF0800"
    WARNING = "#E0A607"
    WARNING_2 = "#FFF911"
    PRIMARY = "#B61E64"
    SECONDARY = "#086655"


type GID = str
type Frequency = Literal["daily", "weekly", "monthly"]
type GoalCompletionType = Literal["binary", "progressive"]
type Confidence = Literal["not confident", "kind of confident", "confident", "very confident", "extremely confident"]



    


GoalNodePos = NewType("GoalNodePos",float)

@dataclass(slots=True)
class GoalStatus:
    compeltion: float|bool
    status: Literal["complete", "inactive", "active", "incomplete"]

@dataclass(slots=True)
class GoalID:
    tree_id: GID 
    node_id: GID
    node_pos: float
    parent_pos: float
    children_pos: list[float]
    sibling_pos: list[float]|None=None
    tree_root: bool=False # true if the node is the root node of the whole tree
    branch_root: bool=False # true if the node is a root node of a inner tree
                            # meaning if goals branch from this node its a root branch






class SuccessScore(NamedTuple):
    completion_percentage: float
    success_intertia: float
    derailment_chance: float
    score: int


@dataclass(slots=True)
class StreakRecord:
    started_on: date 
    last_complete: datetime|date
    last_incomeplte: datetime|date
    longest_completion_streak: int|float
    shortest_completion_streak: int|float
    longest_incompletion_streak: int|float
    shortest_incompletion_streak: int|float
    total_time_spent: int|float|None=None


@dataclass(slots=True)
class Habit:
    id: GoalID
    alias: str
    goal: str
    description: str
    streak_record: StreakRecord 
    priority: int
    difficulty: int
    prerequisite: list[GoalID]
    postrequisite: list[GoalID]
    complete_today: bool
    questions: dict[str,str]|None=None

@dataclass(slots=True)
class BaseGoal:
    id: GoalID
    alias: str
    goal: str
    importance: int|float
    priority: int|float
    difficulty: int|float
    start_date: date|datetime
    due_date: date|datetime
    parent: GoalID
    children: list[GoalID]|GoalID
    info: dict[str,str]
    description: str|None=None


    

    
@dataclass(slots=True)
class Goal:
    id: GoalID
    alias: str
    goal: str
    priority: int
    importance: int
    difficulty: int
    prerequisite: list[GoalID]
    postrequisite: list[GoalID]
    status: tuple[float|bool, GoalStatus]
    goal_type: Literal["binary", "progressive"]
    description: str|None=None
    start_date: datetime|date|None=None
    due_date: datetime|date|None=None
    deadline_confidence: Confidence|None=None
    cross_linked: list[GoalID]|None=None
    if_then_plans: dict[str,str]|None=None
    success_score: SuccessScore|None=None
    child_ids: list[int]|None=None
    questions: dict[str,str]|None=None
    tags: tuple[str]|None=None


    def calculate_score(self):
        ...


    def is_dependent(self):
        if len(self.prerequisite) != 0:
            return True
        return False


@dataclass(slots=True)
class Tasks(Goal):
    reps: int|float|None=None
    reps_left: int|float|None=None




