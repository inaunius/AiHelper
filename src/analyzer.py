import sqlite3
import requests
import json
from typing import List, Dict
from deeppavlov import build_model, configs
from constant_configs import *
from gigachat import GigaChat


deep_pavlov_model = build_model(
	configs.ner.ner_rus_bert, 
	download=True, 
	install=True
)


def _ner_extract(text: str) -> List[Dict]:
	entities = []
	current = None

	# for token in deep_pavlov_model([text]):
	# 	print(token, end="\n\n")
	tokens, tags = deep_pavlov_model([text])

	for token, tag in zip(tokens[0], tags[0]):
		if tag.startswith("B-"):
			if current:
				entities.append(current)
				current = {"type": tag[2:], "text": token}
			elif tag.startswith("I-") and current:
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
	dates = [e["text"] for e in entities if e["type"] == "DATE"]
	orgs = [e["text"] for e in entities if e["type"] == "ORG"]
	laws = [e["text"] for e in entities if e["type"] in ("LAW", "NORMA", "MISC")]

	return {
		"dates": list(set(dates)),
		"orgs": list(set(orgs)),
		"laws": list(set(laws)),
		"raw_entities": entities
	}





# def _ask_yandex_gpt(prompt: str) -> str:
# 	headers = {
# 		"Content-Type": "application/json",
# 		"Authorization": f"Api-Key {YANDEX_API_KEY}"
# 	}
# 	payload = {
# 		"modelUri": "gpt://foundationModels/yandexgpt/latest",
# 		"completionOptions": {"maxTokens": 500, "temperature": 0.2},
# 		"messages": [{"role": "user", "text": prompt}]
# 	}

# 	resp = requests.post(YANDEX_URL, headers=headers, json=payload)
# 	resp.raise_for_status()

# 	return resp.json()["result"]["alternatives"][0]["message"]["text"]

# def _ask_gigachat(prompt: str) -> str:
# 	# headers = {
# 	#     "Authorization": f"Bearer {GIGACHAT_TOKEN}",
# 	#     "Content-Type": "application/json"
# 	# }
# 	# payload = {
# 	#     "model": "GigaChat",
# 	#     "messages": [{"role": "user", "content": prompt}],
# 	#     "temperature": 0.2,
# 	#     "max_tokens": 500
# 	# }
# 	# resp = requests.post(GIGACHAT_URL, headers=headers, json=payload)
# 	# resp.raise_for_status()
		
# 	with GigaChat(credentials=GIGACHAT_TOKEN, verify_ssl_certs=False) as giga:
# 		return giga.chat(prompt).json()["choices"][0]["message"]["content"]

# def _generate_report(changes: List[Dict]) -> str:
# 	formatted = []
# 	for ch in changes:
# 		formatted.append(
# 			f"""
# Название: {ch["title"]}
# URL: {ch["url"]}
# Выделенные даты: {", ".join(ch["analysis"]["dates"]) or "-"}
# Нормативные акты: {", ".join(ch["analysis"]["laws"]) or "-"}
# Организации: {", ".join(ch["analysis"]["orgs"]) or "-"}
# """
# )
# 	prompt = (
# 		"Сформируй аналитический отчёт о законодательных изменениях.\n"
# 		"Структура:\n"
# 		" - краткое содержание изменений\n"
# 		" - ключевые даты\n"
# 		" - упомянутые нормативные акты\n"
# 		" - значимость изменений\n\n"
# 		"Данные:\n" +
# 		"\n".join(formatted)
# 	)

# 	try:
# 		return _ask_yandex_gpt(prompt)
# 	except:
# 		return _ask_gigachat(prompt)
		
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
		print(f"[OK] ANALYZED: {title}")

	print(changes)
	# print("\GENERATING REPORT:\n")
	# report = _generate_report(changes)
	# with open("law_report.txt", "w", encoding="utf-8") as f:
	# 	f.write(report)
	# print("REPORT GENERATED")

