CREATE TABLE goals(
  id INTEGER PRIMARY KEY, 
  tree_id INTEGER NOT NULL,
  node_id INTEGER NOT NULL,
  node_pos REAL NOT NULL,
  parents TEXT, -- id of parent
  siblings TEXT, -- id(s) of sibling(s)
  in_focus INTEGER NOT NULL CHECK(tree_root in (0,1)) DEFAULT 0,
  tree_root INTEGER NOT NULL CHECK(tree_root in (0,1)) DEFAULT 0,
  leaf_node INTEGER NOT NULL CHECK(leaf_node in (0,1)) DEFAULT 0,
  alias TEXT,
  goal TEXT NOT NULL,
  priority REAL NOT NULL, 
  importance REAL NOT NULL DEFAULT 0,
  difficulty REAL NOT NULL,
  prerequisite TEXT,
  postrequisite TEXT,
  status TEXT NOT NULL CHECK(status in ("complete", "in progress", "inactive","active", "incomplete")),
  goal_type TEXT NOT NULL CHECK(goal_type in ("binary", "progressive"),
  description TEXT,
  start_date INTEGER,
  due_date INTEGER NOT NULL,
  deadline_confidence TEXT NOT NULL CHECK(deadline_confidence in ("not confident", "kind of confident", "confident", "very confident", "extremely confident")),
  cross_tree_links INTEGER, -- figure this out !
  connections INTEGER, -- a way for items like images, videos, csv's etc to be linked to a specific node 
  if_then_plans INTEGER,
  questions INTEGER, 
  tags TEXT NOT NULL, -- used to catagorize each goal
  FOREIGN KEY(tree_id) REFERENCES trees(id),
  FOREIGN KEY(if_then_plans) REFERENCES questions(id),
  FOREIGN KEY(questions) REFERENCES questions(id),
  UNIQUE(node_id)
)
  

CREATE TABLE habits(
  id INTEGER PRIMARY KEY,
  goal TEXT NOT NULL,
  description TEXT,
  priority INTEGER,
  frequency_type TEXT NOT NULL CHECK(frequency_type in ("daily","weekly", "monthly", "quarterly", "yearly")),
  goal_connection INTEGER,
  date_started INTEGER NOT NULL,
  next_due_date INTEGER NOT NULL,
  last_complete INTEGER NOT NULL,
  streak_record INTEGER,
  difficulty REAL NOT NULL,
  prerequisite INTEGER,
  postrequisite INTEGER,
  complete_today INTEGER NOT NULL CHECK (complete_today in (0,1)),
  questions INTEGER,
  if_then_plans INTEGER,
  FOREIGN KEY(goal_connection) REFERENCES goals(id)
)


CREATE TABLE tasks(
  id INTEGER PRIMARY KEY,
  goal TEXT NOT NULL, 
  node_connection INTEGER,
  start_date INTEGER,
  due_date INTEGER,
  task_type TEXT NOT NULL CHECK(task_type in ("recursive","binary","trigger")),
)




CREATE TABLE questions(
  id INTEGER NOT NULL, 
  question TEXT NOT NULL, 
  answer TEXT NOT NULL,
  question_type TEXT NOT NULL CHECK(question in ("standard", "if_then"))
)


CREATE TABLE streaks(
  -- a track record of an unbroken run of successful completions under a defined rule
  id INTEGER PRIMARY KEY,
  rule TEXT NOT NULL, -- will likely change rule to a sql query that auto triggers based on a set of params
  connected_goal INTEGER NOT NULL, -- the streak will track against a goal, task or habit 
  best INTEGER,
  best_date INTEGER,
  worst INTEGER,
  worst_date INTEGER,
  average INTEGER,
  average_date INTEGER,
  last INTEGER
)

CREATE TABLE performance_records(
  id INTEGER PRIMARY KEY, 
)

CREATE TABLE trees(
  id INTEGER PRIMARY KEY ,
  root_goal JSON, -- {alias: str|None, goal: str} 
  node_count INTEGER NOT NULL,
  tree_height INTEGER NOT NULL,
  tree_width INTEGER NOT NULL,
  completion_percentage REAL NOT NULL CHECK(completion_percentage >= 0 and completion_percentage <= 100.0),
  success_inertia REAL NOT NULL,
  derailment_chance REAL NOT NULL,
  success_score INTEGER NOT NULL
)



CREATE TABLE saplings(
  id INTEGER PRIMARY KEY,
  alias TEXT, 
  goal TEXT NOT NULL,
  priority INTEGER NOT NULL, 
  importance INTEGER NOT NULL DEFAULT 0,
  difficulty INTEGER NOT NULL,
  prerequisite TEXT,
  postrequisite TEXT,
)
