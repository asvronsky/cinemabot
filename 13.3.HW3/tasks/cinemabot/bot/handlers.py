import logging
from aiogram import Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from .movie_search import search_movie
from .database import log_search, get_history, get_stats

def get_star_rating(rating):
    full_stars = int(rating // 2)
    half_star = 1 if rating % 2 >= 1 else 0
    empty_stars = 5 - full_stars - half_star
    return '★' * full_stars + '⯨' * half_star + '☆' * empty_stars

async def send_welcome(message: types.Message):
    logging.info(f"Received /start command from user {message.from_user.id}")
    welcome_text = (
        "Привет!\nЯ CinemaBot и я могу помочь вам найти информацию о фильмах.\n\n"
        "Вот что я умею:\n"
        "- Просто отправьте мне название фильма, и я найду информацию о нем.\n"
        "- Команда /history покажет вашу историю поиска.\n"
        "- Команда /stats покажет статистику поиска фильмов.\n"
        "- Команда /help покажет это сообщение.\n\n"
        "Примеры запросов:\n"
        "- Venom\n"
        "- остров собак\n"
        "- магия лунного света\n"
        "- Мстители: война бесконечности\n"
        "- город в котором меня нет\n"
        "- как витька чеснок вез леху штыря в дом инвалидов"
    )
    await message.answer(welcome_text)

async def send_help(message: types.Message):
    logging.info(f"Received /help command from user {message.from_user.id}")
    help_text = (
        "Я CinemaBot и я могу помочь вам найти информацию о фильмах.\n\n"
        "Вот что я умею:\n"
        "- Просто отправьте мне название фильма, и я найду информацию о нем.\n"
        "- Команда /history покажет вашу историю поиска.\n"
        "- Команда /stats покажет статистику поиска фильмов.\n"
        "- Команда /help покажет это сообщение.\n\n"
        "Примеры запросов:\n"
        "- Venom\n"
        "- остров собак\n"
        "- магия лунного света\n"
        "- Мстители: война бесконечности\n"
        "- город в котором меня нет\n"
        "- как витька чеснок вез леху штыря в дом инвалидов"
    )
    await message.answer(help_text)

async def search_and_send_movie(message: types.Message):
    logging.info(f"Received search query '{message.text}' from user {message.from_user.id}")
    movie_details = await search_movie(message.text)
    if movie_details:
        await log_search(message.from_user.id, message.text)
        star_rating = get_star_rating(movie_details['rating'])
        kinopoisk_url = f"https://www.kinopoisk.ru/film/{movie_details['id']}/"
        response_text = (
            f'<b>Название</b>: <a href="{kinopoisk_url}">{movie_details["title"]}</a>\n'
            f"<b>Рейтинг</b>: {star_rating} ({movie_details['rating']})\n"
            f"<b>Описание</b>: {movie_details['description']}"
        )
        if movie_details['fact']:
            response_text += f"\n<b>Интересный факт</b>: {movie_details['fact']}"
        if movie_details['review_title']:
            response_text += f"\n<b>Отзыв</b>: {movie_details['review_title']}"
        if movie_details['online_viewing_link']:
            response_text += f'\n<b>Смотреть онлайн</b>: <a href="{movie_details["online_viewing_link"]}">{movie_details["online_viewing_title"]}</a>'
        
        await message.answer_photo(photo=movie_details['poster'], caption=response_text, parse_mode="HTML")
        logging.info(f"Sent movie details for '{message.text}' to user {message.from_user.id}")
    else:
        await message.answer("Извините, я не смог найти фильм по вашему запросу.")
        logging.info(f"No movie found for query '{message.text}' from user {message.from_user.id}")

async def show_history(message: types.Message):
    logging.info(f"Received /history command from user {message.from_user.id}")
    history = await get_history(message.from_user.id)
    if history:
        history_text = "\n".join([f"{item[0]} в {item[1]}" for item in history])
        await message.answer(f"Ваша история поиска:\n{history_text}")
    else:
        await message.answer("У вас нет истории поиска.")
        logging.info(f"No search history found for user {message.from_user.id}")

async def show_stats(message: types.Message):
    logging.info(f"Received /stats command from user {message.from_user.id}")
    stats = await get_stats()
    stats_text = "\n".join([f"{item[0]}: {item[1]} поисков" for item in stats])
    await message.answer(f"Статистика поиска:\n{stats_text}")

def register_handlers(dp: Dispatcher):
    dp.message.register(send_welcome, Command(commands=["start"]))
    dp.message.register(send_help, Command(commands=["help"]))
    dp.message.register(show_history, Command(commands=["history"]))
    dp.message.register(show_stats, Command(commands=["stats"]))
    dp.message.register(search_and_send_movie, F.text)
    logging.info("Handlers registered.")

