import builtins
from secrets import choice
import string
from datetime import date, datetime, time
from rich.live import Live
from custom_types import DatePrompt, IntegerPrompt, TimePrompt
from rich.prompt import Confirm, FloatPrompt, IntPrompt, InvalidResponse, Prompt
from custom_types import ConfidenceLevel, Question
from rich.text import Text
from rich.console import Console 

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
            "name": "starting",
            "answer_type": time,
            "question": "when will you start ??"
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


answers = {}



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


# will add this multi select feature later, not enough time to worry about this type of stuff now
# def multi_select_prompt(question: Text, choices: list[str|int|float], lettered_choices: bool=False):
#     choice_num_len = 1
#     choice_enum_space = choice_num_len + 2
#     new_question = show_selections(question.copy(), choices, lettered_choices)
#     original_question = new_question.copy()
#     clrs = ["#FA5307","#FA0727", "#07FA8D","#FA34EC"]
#     with Live(question, console=console, refresh_per_second=4) as live:
#         while True:
#             start_pos = len(str(question)) + 1
#             first_choice_len = len(str(choices[0])) + choice_num_len + 2
#             end_pos = start_pos + first_choice_len
#             for idx,choice in enumerate(choices):
#                 if (idx + 1) > 9: 
#                     choice_enum_space = choice_enum_space + 1
#                 if idx != 0:
#                     curr_choice_len = len(str(choice)) + choice_enum_space
#                     start_pos += len(str(choices[idx - 1])) + choice_enum_space + 1 
#                     end_pos = start_pos + curr_choice_len + 1
#                 new_question = original_question.copy()
#                 new_question.stylize(style=f"on {clrs[idx%2]} bold underline", start=start_pos,
#                                      end=end_pos)
#                 live.update(new_question)
#                 sleep(1)
#
#
# def raw_input_mode():
#     fd = sys.stdin.fileno()
#     old = termios.tcgetattr(fd)
#     new = termios.tcgetattr(fd)
#     new[3] = new[3] & ~termios.ECHO          # lflags
#     try:
#         termios.tcsetattr(fd, termios.TCSADRAIN, new)
#     finally:
#         termios.tcsetattr(fd, termios.TCSADRAIN, old)
#     return 
    


 
def ask_questions():
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







ask_questions()





