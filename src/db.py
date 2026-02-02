from platform import java_ver
import sqlite3 as sqlite
from typing import Any, Callable


def connect_to_db(password: str):
    conn = sqlite.connect("db")
    return conn

def db_connection(db: str="main"):
    ...

def db_select(query: str, return_type: type, data_converter: Callable,
              conn: sqlite.Connection):
    ...

def db_insert(query: str, data: Any, conn: sqlite.Connection):
    ...


def db_update(query: str, data: Any, conn: sqlite.Connection):
    ...



def db_delete(query: str, data: Any, conn: sqlite.Connection):
    ...

def main():
    ...




if __name__ == "__main__":
    main()


