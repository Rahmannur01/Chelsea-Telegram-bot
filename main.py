import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from MSportParser import MSportChelsea
from PostgreSQLData import DBChelsea
from logger import logger

base_path = Path(__file__).resolve().parent
load_dotenv()

#session = AiohttpSession(proxy="http://127.0.0.1:10801")
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()

dbChelsea = DBChelsea()

def main_menu():
    kb = [
        [
            types.KeyboardButton(text="Новости"), 
            types.KeyboardButton(text="Следующие матчи")
        ],
        [
            types.KeyboardButton(text="Прошедшие матчи"), 
            types.KeyboardButton(text="Таблица")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard

@dp.message(Command('start'))
async def start_command(message : types.Message):
    text = (
        "💙 <b>Добро пожаловать в Chelsea Fan Bot</b>\n\n"
        "Здесь ты можешь узнать всё о любимом клубе:\n\n"
        "📰 <b>Новости</b>\n"
        "⚽ <b>Матчи</b>\n"
        "🏆 <b>Таблица</b>\n\n"
        "Выбери нужный раздел 👇"
    )
    await message.answer(text, 
        parse_mode=ParseMode.HTML, 
        reply_markup=main_menu()
    )

    logger.info("Command: start")

@dp.message(F.text.lower() == "новости")
async def cmd_news(message : types.Message):
    try:
        await message.answer("Поиск новостей...")

        news_rows = await dbChelsea.get_news()
        new_message = ""

        if news_rows is not None:
            for news_row in news_rows:
                new_message += f"<b>{news_row['date']} {news_row['time']}</b>\n{news_row['text']}\n\n"

            await message.answer(new_message, parse_mode=ParseMode.HTML)
            logger.info("Command: news")
            return
    except Exception as e:
        logger.error(str(e))
    
    await message.answer("Что то пошло не так, повторите пожалуйста", reply_markup=main_menu())

@dp.message(F.text.lower() == "прошедшие матчи")
async def cmd_prev_games(message : types.Message):
    try:
        await bot.send_message(message.chat.id, "Идёт поиск...")
        matches = await dbChelsea.get_prev_games()
            
        if matches != None:
            new_message = ""
            for i in range(len(matches)):
                new_message += f"⚽️ {matches[i]['first_team']} 🆚 {matches[i]['second_team']} -> <b>{matches[i]['score']}</b>\n⏰ {matches[i]['datetime']} {matches[i]['day_of_week']}\n🏆 {matches[i]['tournament_name']}\n\n"

            await message.answer(new_message, parse_mode=ParseMode.HTML)
            logger.info("Command: prev matches")
            return
    except Exception as e:
        logger.error(str(e)) 

    await message.answer("Что то пошло не так, повторите пожалуйста", reply_markup=main_menu())

@dp.message(F.text.lower() == "следующие матчи")
async def cmd_next_games(message : types.Message):
    try:
        await bot.send_message(message.chat.id, "Идёт поиск...")
        matches = await dbChelsea.get_next_games()
        
        if matches is not None:
            new_message = ""

            for i in range(len(matches)):
                new_message += f"<b>⚽️ {matches[i]['first_team']} 🆚 {matches[i]['second_team']}\n⏰ {matches[i]['datetime']} {matches[i]['day_of_week']}\n🏆 {matches[i]['tournament_name']}</b>\n\n"
            await message.answer(new_message, parse_mode=ParseMode.HTML)
            logger.info("Command: next matches")
            return
    except Exception as e:
        logger.error(str(e))

    await message.answer("Что то пошло не так, повторите пожалуйста", reply_markup=main_menu())

@dp.message(F.text.lower() == "таблица")
async def cmd_table(message : types.Message):
    try:
        await bot.send_message(message.chat.id, "Идёт поиск...")
        teams = await dbChelsea.get_EPL_table()
        
        if teams is not None:
            new_message = "<b>Турнирная таблица АПЛ</b>\n\n<pre>"

            # задаём ширину колонок
            place_width = 3
            name_width = 18
            score_width = 2

            for team in teams:
                place = str(team['place']).ljust(place_width)
                name = team['name'].ljust(name_width)
                score = str(team['score']).rjust(score_width)

                if team['name'] == 'Челси':
                    # выделяем жирным внутри <pre>
                    name = f"<b>{name}</b>"
                    score = f"<b>{score}</b>"

                new_message += f"{place} {name} {score}\n"

            new_message += "</pre>"

            await message.answer(new_message, parse_mode="HTML")
            logger.info("Command: table")
            return
    except Exception as e:
        logger.error(str(e))

    await message.answer("Что то пошло не так, повторите пожалуйста", reply_markup=main_menu())


async def main():
    try:
        await dbChelsea.connect()
        await dp.start_polling(bot)
        logger.info("Start")
    finally:
        await dbChelsea.close()
        await bot.close()
        logger.info("Close")

if __name__ == "__main__":
   asyncio.run(main())