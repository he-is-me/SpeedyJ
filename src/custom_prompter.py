from abc import abstractmethod
from typing import Any, Optional, TextIO
from rich.live import Live
from rich.text import Text
from rich.console import Console


_console = Console(color_system="truecolor")


class QuestionPromptBase:
    response_type: type = str
    err_msg: dict[str,str|Text] = {}
    prompt_suffix = ": "


    def __init__(self,
                 prompt: str="",
                 *,
                 console: Console =_console,
                 stream: TextIO | None = None,
                 live_instance: Optional[Live] = None,
                 password: bool= False,
                 case_sensitive: bool= False,
                 emoji: bool = True,
                 markup: bool = False,
                 show_default: bool= False,
                 show_choices: bool= False):

        self.prompt = prompt 
        self.stream = stream
        self.console = _console
        if live_instance is not None:
            self.live_instance = live_instance

        self.case_sensitive = case_sensitive
        self.show_default = show_default
        self.show_choices = show_choices


        @abstractmethod
        def process_response(self, value: str) -> bool:
            pass

        def ask(self):
            if live_instance is not None:
                ...

            value = _console.input(self.prompt,
                                   password=self.password,
                                   emoji=self.emoji,
                                   markup=self.markup,
                                   stream=self.stream
                                   )

            
            return value

