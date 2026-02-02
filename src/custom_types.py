from types import FunctionType
from typing import Any, NamedTuple, Literal, NewType, Text, TypeAlias, TypedDict, Callable
from enum import StrEnum
from datetime import date, datetime, time 
from dataclasses import dataclass


type QuestionType = Literal["text", "confirm", "select", "print", "search"]
type AnswerType = type[str|bool|int|float|date|datetime|time|list[str]]
type NodeInfoArray = list[NodeInfo]
ConfidenceLevel = {"not confident", "kind of confident", "confident", "very confident", "extremely confident"}


@dataclass(slots=True)
class NodeInfo:
    tree_id: int
    node_id: int
    node_pos: float

@dataclass(slots=True)
class NodeConnection:
    connection_type: Literal["image", "document", "video"]
    connected_to: NodeInfo


@dataclass(slots=False)
class TimeInfo:
    hours: int=0
    minute: int=0
    second: int=0
    microsecond: int=0

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




