import os
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv
from markdown import markdown
from bs4 import BeautifulSoup


load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL")

bot = Bot(token=BOT_TOKEN)


async def telegram_markdown(text: str):
    html = markdown(text, output_format="html")

    ALLOWED = {"b", "i", "u", "s", "a", "code", "pre", "blockquote", "blockquote expandable"}

    soup = BeautifulSoup(html, "html.parser")

    for tag in list(soup.find_all()):
        name = tag.name.lower()
        if name in ALLOWED:
            if name == "a":
                tag.attrs = {"href": tag.attrs["href"]}
            else:
                tag.attrs = {}
        else:
            tag.unwrap()

    return str(soup)



async def send_text(message: str):
    parts = [f"Отчёт отправлен {datetime.now().isoformat()}\n\n"]

    for line in message.split("\n"):
        if len(parts[-1]) + len(line) < 4000:
            parts[-1] += line + "\n"
        else:
            parts += [line]

    for part in parts:
        result = await bot.send_message(
            chat_id=CHANNEL,
            text=await telegram_markdown(part),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    return result


async def main():
    TEST = False

    if not TEST:
        from parse import parse_all_to_db
        from analyzer import analyze_all

    message = ""

    try:
        if not TEST:
            if not path.exists(DB_PATH):
                parse_all_to_db()
            analyze_all()

        with open("analyze.txt") as f:
            message += f.read()
    except Exception as err:
        message += f"Unexpected {err=}, {type(err)=}\n"

    if message == "":
        message += "Unexpected unexpected"

    await send_text(message)


if __name__ == "__main__":
    asyncio.run(main())
