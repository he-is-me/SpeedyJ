import builtins
import string
from datetime import date, datetime, time
from rich import print as rprint
from rich.live import Live
from rich.prompt import Confirm, FloatPrompt, IntPrompt, InvalidResponse, Prompt
from custom_types import ConfidenceLevel, Question
from rich.text import Text
from rich.console import Console 
from enum import StrEnum
from rich.prompt import Confirm, IntPrompt, InvalidResponse, PromptBase
from datetime import date, datetime, time, timezone

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


    def unit_in_value(self, value: str):
        for unit in self.units:
            if unit in value:
                return unit
        return False

    def determine_unit(self,value: str):
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
        return unit


    def split_time_units(self, value: str, unit: str):
        time_info = {}
        unit_idx = self.units.index(unit)
        if unit + "s" in value: 
            value = value.replace(unit + "s", "")
        value = value.replace(unit, "")
        if value.find(":") == -1 and value.find(".") == -1:
            split_units = value
        elif unit == "second" or unit == "microsecond":
            split_units = value.split(".")
        elif value.find("."):
            split_units = value.split(":") + value.split(".")
        else:
            split_units = value.split(":") 
        for idx,time_unit in enumerate(self.units[unit_idx:]):
            try:
                time_info[time_unit] = split_units[idx]
            except Exception:
                break
        rprint(time_info)
        return time_info

        




    def validate_time_unit(self, value: str):
        if not (unit := self.unit_in_value(value)):
            unit = self.determine_unit(value)
        time_info = self.split_time_units(value,unit)
        return time(*time_info)


    def process_response(self, value: str, confirm_time: bool=True) -> time: # pyright: ignore[]
        return self.validate_time_unit(value)




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


console = Console(color_system="truecolor")

QUESTIONS: dict[str, list[Question]] = {
    "new_goal": [
        {
            "type": "print",
            "name": "",
            "answer_type": str,
            "question": "[bold #DB0202 underline]The Journey[/] Of [bold green]1000 Miles Starts With A Single Step. - Lao Tzu" #NOTE: add random quote generator
        },
        {
            "type": "text",
            "name": "goal",
            "answer_type": str,
            "question": "What is the intent of this goal ?"
        },
        {
            "type": "confirm", 
            "name": "alias?",
            "answer_type": bool,
            "question": "Would you to make an alias for this goal ?" 
        },
        {
            "type": "text", 
            "name": "alias",
            "answer_type": str,
            "question": "What will the alias be ?" ,
            "when": lambda x: x["alias?"] is True
        },
        {
            "type": "text",
            "name": "priority",
            "answer_type": int,
            "question": "priority of this goal (1-10) ?"
        },
        {
            "type": "text",
            "name": "importance",
            "answer_type": int,
            "question": "importance of this goal (1-10) ?"
        },
        {
            "type": "text",
            "name": "difficulty",
            "answer_type": int,
            "question": "difficulty of this goal (1-10) ?"
        },
        {
            "type": "text",
            "name": "start_date",
            "answer_type": date,
            "question": "when will you start this goal ?"
        },
        {
            "type": "text",
            "name": "due_date",
            "answer_type": date,
            "question": "when do you expect or hope to finish ?"
        },
        {
            "type": "select",
            "name": "deadline_confidence",
            "question": "how confident are you in accomplishing this goal by the deadline ?",
            "answer_type": str,
            "choices": list(ConfidenceLevel) 
        },
    ]
}





def date_prompt(return_as: type[str|date|datetime]=date):
    chosen_date = DatePrompt().ask("when are you gonna start ?", choices=["now", "later"])
    if chosen_date == datetime(1,1,1,1,1,1,1):
        console.print("will decide later")
        return None
    else:
        return chosen_date


def time_prompt(confirm: bool=False):
    return TimePrompt().ask("time ?")

def get_prompter(answer_type,question,kwarg_dict):
    match answer_type:
        case builtins.str:
            console.print("returning str prompter !")
            return Prompt().ask(question, **kwarg_dict)
        case builtins.bool:
            console.print("returning bool prompter !")
            return Confirm().ask(question, **kwarg_dict)
        case builtins.int:
            console.print("returning int prompter !")
            return IntPrompt.ask(question, **kwarg_dict)
        case builtins.float:
            console.print("returning floatprompter !")
            return FloatPrompt.ask(question, **kwarg_dict)
        case a if a is date | datetime:
            return date_prompt()
        case a if a is time:
            return time_prompt()    


def loop_prompter(question: Question):
    assert "answer_type" in question
    assert "question" in question
    assert "validator" in question

    while True:
        result = get_prompter(question["answer_type"],
                                question["question"],
                                question["kwargs"] if "kwargs" in question else {} 
                                )
        if not question["validator"]["func"](result):
            console.print(question["validator"]["error_msg"])
            continue
        else:
            return result
        

def show_selections(question: Text, choices: list[str|int|float], lettered_choices: bool=False):
    if len(choices) > 27:
        raise ValueError("Too many choices, use search instead")
    for idx,choice in enumerate(choices,1):
        if not lettered_choices:
            question = question.append_text(Text(f"\n{idx}. {choice}"))
        else:
            import string
            question = question.append_text(Text(f"\n{string.ascii_lowercase[idx - 1]}. {choice}"))
    return question



def confirm_selection(answer):
    return Confirm().ask(f"confirm selection: {answer}")




def get_integer_choice(choice_count: int):
    answer = IntegerPrompt.ask("choice (enter Q to quit)")
    if answer == "Q":
        return answer
    if answer > choice_count or answer <= 0:
        console.print(f"{answer} is out of range ! (1-{choice_count} only)")
    elif answer == "Q":
        return answer 
    else:
        return (answer - 1)

def get_lettered_choice(choice_count: int):
    possible_choices = list(string.ascii_lowercase)[0: choice_count]
    answer = Prompt.ask("choice (enter Q to quit)")
    if answer == "Q":
        return answer 
    if len(answer) > 1 or answer not in possible_choices: 
        console.print("Invalid choice !")
    else:
        return possible_choices.index(answer)


def highlight_choice(text: Text,choice: str, live_instance: Live, selected_choices: list[str]):
    if choice in selected_choices:
        text.spans.clear()
        selected_choices.remove(choice)
        text.highlight_words(selected_choices, "bold black on #FFDA00")
        return text 
    else:
        text.highlight_words([choice], "bold black on #FFDA00") #NOTE: switch to enum const value
        selected_choices.append(choice)
        return text


def multi_select_prompt(question: Text, choices: list[str|Text], lettered_choices: bool=False,
                        confirm: bool=True, skippable: bool=False, min_choices: int=2,
                        max_choices: int=2):

    selected_choices = []
    for idx,choice in enumerate(choices, 1):
        if lettered_choices:
            possible_choices = list(string.ascii_lowercase)
            question.append_text(Text(f"\n{possible_choices[idx - 1]}. {choice}"))
        else:
            question.append_text(Text(f"\n{idx}. {choice}"))
    question.append_text(Text("\n\n"))

    with Live(question,console=console,auto_refresh=False, transient=True) as live:
        while True:
            if lettered_choices:
                answer = get_lettered_choice(len(choices))
            else:
                answer = get_integer_choice(len(choices))
            if answer is None:
                continue
            if answer == "Q":
                if skippable and len(selected_choices) == 0: 
                    return None
                elif skippable and len(selected_choices) > 0:
                    break
                if not skippable and (len(selected_choices) >= min_choices and
                    len(selected_choices) <= max_choices):
                    break
                else:
                    console.print(f"Too {"few" if len(selected_choices) < min_choices else "many"} choices selected")
                    if len(selected_choices) > max_choices:
                        console.print(f"This question requires no more than {max_choices} choices")
                    if len(selected_choices) < min_choices:
                        console.print(f"This question requires at least {min_choices} {"choice" if min_choices == 1 else "choices"}")
                    live.refresh()
            else:
                # question.highlight_words([str(choices[answer])], "bold black on #FFDA00")#NOTE: switch to enum const value
                question = highlight_choice(question, str(choices[answer]), live, selected_choices)
                live.console.clear()
                live.update(question, refresh=True)

    console.print(*selected_choices)
    return selected_choices
                




def single_select_prompt(question: Text, choices: list[str|Text], lettered_choices: bool=False,
                         confirm_choice: bool=True, skippable: bool=False, minimum_choices: int=0):
    console.print(question)
    answer_range = 0
    for idx,choice in enumerate(choices, 1):
        if lettered_choices:
            answer_range = [x for x in string.ascii_lowercase]
            console.print(f"{answer_range[idx - 1]}. {choice}")
        else:
            console.print(f"{idx}. {choice}")
            answer_range = range(1,len(choices))
    console.print("done")

    while True:
        if lettered_choices:
            answer = get_lettered_choice(len(choices))
        else:
            answer = get_integer_choice(len(choices))
        if answer is None:
            continue
        if confirm_choice:
            confirmed = Confirm().ask(f"Are you sure you want to select {answer} !")
            if not confirmed:
                continue
        break
    console.print("DONE!")


 
def ask_questions():
    answers = {}
    for question in QUESTIONS["new_goal"]:
        assert "type" in question
        assert "question" in question
        assert "name" in question
        assert "answer_type" in question
        if "when" in question:
            ...
        if question["type"] == "print":
            console.print(question["question"])
            continue
        elif question["type"] == "search":
            ...
        elif question["type"] == "select" and question["answer_type"] is list:
            if "choices" not in question: 
                raise ValueError("no choices provided for select type !")
            multi_select_prompt(Text(question["question"]), question["choices"])
        else:
            if "validator" in question and question["validator"]["loop_until_correct"]:
                result = loop_prompter(question)
            else:
                result = get_prompter(question["answer_type"],
                                        question["question"],
                                        question["kwargs"] if "kwargs" in question else {} 
                                        )
            answers[question["name"]] = result







# ask_questions()





