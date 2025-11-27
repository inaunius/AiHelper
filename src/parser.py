import requests
import sqlite3
import xml.etree.ElementTree as ET

RSS_URL = "https://www.consultant.ru/rss/hotdocs.xml"


def _fetch_rss() -> str:
    resp = requests.get(RSS_URL)
    resp.raise_for_status()
    return resp.text


def _parse_rss(xml_text: str) -> list:
    root = ET.fromstring(xml_text)
    items = []

    for item in root.findall("./channel/item"):
        title = item.find("title").text
        link = item.find("link").text
        pub_date = item.find("pubDate").text
        description = item.find("description").text if item.find("description") is not None else ""

        items.append({
            "title": title,
            "url": link,
            "date": pub_date,
            "description": description
        })

    return items


def _create_connection(path: str) -> sqlite3.Connection:
    return sqlite3.connect(path)


def _create_table(conn):
    query = """
    CREATE TABLE IF NOT EXISTS law_changes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT UNIQUE,
        date TEXT,
        description TEXT
    );
    """
    conn.execute(query)
    conn.commit()


def _insert_changes(conn: sqlite3.Connection, item) -> None:
    query = """
    INSERT OR IGNORE INTO law_changes (title, url, date, description)
    VALUES (?, ?, ?, ?);
    """
    conn.execute(query, (item["title"], item["url"], item["date"], item["description"]))
    conn.commit()


def parse_all_to_db() -> None:
    conn = _create_connection(r"laws.db")
    _create_table(conn)

    xml_text = _fetch_rss()
    items = _parse_rss(xml_text)

    for item in items:
        _insert_changes(conn, item)
        print("Добавлено:", item["title"])