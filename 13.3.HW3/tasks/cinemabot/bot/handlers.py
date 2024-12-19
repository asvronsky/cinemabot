import logging
from aiogram import Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from .movie_search import search_movie
from .database import log_search, get_history, get_stats

async def send_welcome(message: types.Message):
    logging.info(f"Received /start or /help command from user {message.from_user.id}")
    await message.answer("Hi!\nI'm CinemaBot!\nPowered by aiogram.")

async def search_and_send_movie(message: types.Message):
    logging.info(f"Received search query '{message.text}' from user {message.from_user.id}")
    movie_details = await search_movie(message.text)
    if (movie_details):
        await log_search(message.from_user.id, message.text)
        await message.answer(f"Title: {movie_details['title']}\nRating: {movie_details['rating']}\nPoster: {movie_details['poster']}")
        logging.info(f"Sent movie details for '{message.text}' to user {message.from_user.id}")
    else:
        await message.answer("Sorry, I couldn't find any movie matching your query.")
        logging.info(f"No movie found for query '{message.text}' from user {message.from_user.id}")

async def show_history(message: types.Message):
    logging.info(f"Received /history command from user {message.from_user.id}")
    history = await get_history(message.from_user.id)
    history_text = "\n".join([f"{item[0]} at {item[1]}" for item in history])
    await message.answer(f"Your search history:\n{history_text}")

async def show_stats(message: types.Message):
    logging.info(f"Received /stats command from user {message.from_user.id}")
    stats = await get_stats()
    stats_text = "\n".join([f"{item[0]}: {item[1]} searches" for item in stats])
    await message.answer(f"Search statistics:\n{stats_text}")

def register_handlers(dp: Dispatcher):
    dp.message.register(send_welcome, Command(commands=["start", "help"]))
    dp.message.register(search_and_send_movie, F.text)
    dp.message.register(show_history, Command(commands=["history"]))
    dp.message.register(show_stats, Command(commands=["stats"]))
    logging.info("Handlers registered.")

