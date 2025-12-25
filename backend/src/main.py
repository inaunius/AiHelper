from os import path
import sqlite3
import os
from dotenv import load_dotenv
from constant_configs import *
from parse import parse_all_to_db
from analyzer import analyze_all


if __name__ == "__main__":
	load_dotenv()
	print(os.getenv(LOCAL_OLLAMA_NAME_KEY))
	print(os.getenv(LOCAL_OLLAMA_URL_KEY))

	if not path.exists(DB_PATH):
		parse_all_to_db()
	analyze_all()
	