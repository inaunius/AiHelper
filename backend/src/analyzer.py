import sqlite3
import requests
import os
import json
from typing import List, Dict
from deeppavlov import build_model, configs
from constant_configs import *
from gigachat import GigaChat
from datetime import datetime
from dotenv import load_dotenv


DATA_TYPE = "DATE"
ORG_TYPE = "ORG"
LOC_TYPE = "LOC"
LAW_TYPES = ("LAW", "NORMA", "MISC")


UNKNOWN_TAG = "O"
BEGIN_TAG_PREFIX = "B-"
IN_TAG_PREFIX = "I-"

deep_pavlov_model = build_model(
	configs.ner.ner_rus_bert, 
	download=True, 
	install=True
)

def _make_report(data: List[Dict]) -> str:
	load_dotenv()

	prompt = ANALYZE_PROMPT_BEGINNING + str(data)	
	payload = {
  	"model": "mistral:7b",
  	"prompt": prompt,
		"system": "Ты - российский юрист. Ты отвечаешь только на русском.",
  	"stream": False
	}

	response = requests.post(LOCAL_OLLAMA_URL, json=payload)
	print("ANSWERED: " + response.json()["response"])
	return response.json()["response"]

def _ner_extract(text: str) -> List[Dict]:
	entities = []
	current = None

	tokens, tags = deep_pavlov_model([text])
	for token, tag in zip(tokens[0], tags[0]):
		if tag == UNKNOWN_TAG:
			continue
		
		if tag.startswith(BEGIN_TAG_PREFIX):
			if current:
				entities.append(current)
			current = { "type": tag[2:], "text": token }
		
		elif tag.startswith(IN_TAG_PREFIX) and current:
			current["text"] += " " + token
		
		else:
				if current:
					entities.append(current)
					current = None

		if current:
				entities.append(current)

	return entities

def _extract_key_changes(description: str, title: str) -> Dict:
	text = f"{title}. {description}"
	entities = _ner_extract(text)

	dates = [entity["text"] for entity in entities if entity["type"] == DATA_TYPE]
	orgs = [entity["text"] for entity in entities if entity["type"] == ORG_TYPE]
	locs = [entity["text"] for entity in entities if entity["type"] == LOC_TYPE]
	laws = [entity["text"] for entity in entities if entity["type"] in LAW_TYPES]

	return {
		"dates": list(set(dates)),
		"orgs": list(set(orgs)),
		"laws": list(set(laws)),
		"locs": list(set(locs)),
		"raw_entities": entities
	}

def _save_report(changes: str) -> None:
	with open(f"analyze.txt", "w", encoding="utf-8") as dump_file:
		dump_file.write(changes)

def analyze_all():
	connection = sqlite3.connect(DB_PATH)
	cursor = connection.cursor()
	cursor.execute("SELECT title, url, date, description FROM law_changes;")
	rows = cursor.fetchall()
	changes = []
	
	for title, url, date, description in rows:
		analysis = _extract_key_changes(description, title)
		changes.append({
			"title": title,
			"url": url,
			"date": date,
			"description": description,
			"analysis": analysis
		})
		print(f"ANALYZED: {title}")

	
	_save_report(_make_report(changes))