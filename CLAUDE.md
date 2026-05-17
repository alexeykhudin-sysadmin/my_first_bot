# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Telegram-бот на aiogram 3 (async). Виртуальное окружение — Python 3.14, папка `.venv/`.

## Structure

```
bot.py            # Entry point — создаёт Bot, Dispatcher, запускает polling
config.py         # Читает BOT_TOKEN из .env через python-dotenv
handlers/
  common.py       # Роутер с базовыми командами /start и /help
```

Новые обработчики добавляются как отдельные модули в `handlers/`, каждый создаёт свой `Router`, который подключается в `bot.py` через `dp.include_router(...)`.

## Environment Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Вставить BOT_TOKEN в .env
```

## Running

```bash
python bot.py
```
