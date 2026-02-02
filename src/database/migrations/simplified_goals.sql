PRAGMA foreign_keys = ON;


CREATE TABLE trees(
  id INTEGER PRIMARY KEY ,
  tree_id INTEGER NOT NULL,
  root_node INTEGER NOT NULL,
  goal TEXT NOT NULL,
  node_count INTEGER NOT NULL,
  tree_height INTEGER NOT NULL,
  tree_width INTEGER NOT NULL,
  completion_percentage REAL NOT NULL CHECK(completion_percentage >= 0 and completion_percentage <= 100.0)
)


CREATE TABLE nodes(
  id INTEGER PRIMARY KEY,
  tree_id INTEGER NOT NULL,
  node_id INTEGER NOT NULL,
  parent_id INTEGER NOT NULL,
  node_pos REAL NOT NULL,
  goal_type TEXT NOT NULL CHECK(goal_type in ("goal", "task", "recursive task")),
  goal_info JSON, -- this is where all other arbitrary but relavent info goes 
  status TEXT NOT NULL CHECK(status in ("complete", "incomplete", "locked", "in progress")) DEFAULT "incomplete",
  prerequisite TEXT,
  postrequisite TEXT,
  intent TEXT NOT NULL,
  priority NUMERIC NOT NULL DEFAULT 0, 
  importance NUMERIC NOT NULL DEFAULT 0,
  difficulty NUMERIC NOT NULL DEFAULT 0,
  start_date INTEGER,
  due_date INTEGER, 
  days_past_due INTEGER NOT NULL DEFAULT 0,
  days_until_due INTEGER NOT NULL,
  description TEXT,
  post_completion_info INTEGER,
  siblings TEXT,
  children TEXT
)



CREATE TABLE habits(
  id INTEGER PRIMARY KEY,
  goal TEXT NOT NULL,
  priority NUMERIC,
  importance NUMERIC,
  difficulty NUMERIC,
  description TEXT,
  FOREIGN KEY(parent_id) REFERENCES goals(node_id)
  FOREIGN KEY(tree_id) REFERENCES goals(tree_id)
  UNIQUE(node_id)
)



CREATE TABLE connections(
  id INTEGER PRIMARY KEY,
  connection_id INTEGER,
  file_type TEXT NOT NULL CHECK(file_type in ("image", "document", "video", "audio")),
  title TEXT NOT NULL,
  FOREIGN KEY(connection_id) REFERENCES goals(id)
)

