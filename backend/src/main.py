from os import path
import sqlite3
from constant_configs import *
from parse import parse_all_to_db
from analyzer import analyze_all


if __name__ == "__main__":
	if not path.exists(DB_PATH):
		parse_all_to_db()
	analyze_all()
	