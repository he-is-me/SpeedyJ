from rich.text import Text

USER_QUESTIONS = {
    "new goal": (
        {
            "name": "goal_name",
            "question": "what is the intent of this goal ?",
            "ret_type": str,
        },
        {
            "name": "start",
            "question": "when will this start ?",
            "ret_type": str,
        },
        {
            "name": "due",
            "question": "when will this be due ?",
            "ret_type": str,
        },
    )
}
