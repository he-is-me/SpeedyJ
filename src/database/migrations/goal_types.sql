CREATE TABLE goals(
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  goal_type TEXT NOT NULL CHECK(goal_type in ("campaign", "operation", "mission", "objective", "task", "habit")),
  code_name TEXT DEFAULT "none",
)
