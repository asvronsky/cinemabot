import logging
from aiogram import Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from .movie_search import search_movie
from .database import log_search, get_history, get_user_stats, get_global_stats
from datetime import datetime

ANONYMOUS_MESSAGE = ("Извините, я не могу выполнить "
                     "эту команду для анонимных пользователей.")


def get_star_rating(rating: float) -> str:
    """
    Convert a numeric rating to a star rating.

    :param rating: The numeric rating.
    :return: The star rating.
    """
    full_stars = int(rating // 2)
    half_star = 1 if rating % 2 >= 1 else 0
    empty_stars = 5 - full_stars - half_star
    return '★' * full_stars + '⯨' * half_star + '☆' * empty_stars


def format_time_ago(timestamp: str) -> str:
    """
    Format a timestamp as a relative time string.

    :param timestamp: The timestamp to format.
    :return: The formatted relative time string.
    """
    now = datetime.now()
    diff = now - datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    seconds = diff.total_seconds()
    if seconds < 60:
        return f"{int(seconds)} секунд назад"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        if 11 <= minutes <= 19:
            return f"{minutes} минут назад"
        elif minutes % 10 == 1:
            return f"{minutes} минуту назад"
        elif 2 <= minutes % 10 <= 4:
            return f"{minutes} минуты назад"
        else:
            return f"{minutes} минут назад"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        if 11 <= hours <= 19:
            return f"{hours} часов назад"
        elif hours % 10 == 1:
            return f"{hours} час назад"
        elif 2 <= hours % 10 <= 4:
            return f"{hours} часа назад"
        else:
            return f"{hours} часов назад"
    else:
        days = int(seconds // 86400)
        if 11 <= days <= 19:
            return f"{days} дней назад"
        elif days % 10 == 1:
            return f"{days} день назад"
        elif 2 <= days % 10 <= 4:
            return f"{days} дня назад"
        else:
            return f"{days} дней назад"


async def send_welcome(message: types.Message) -> None:
    """
    Send a welcome message to the user.

    :param message: The message object.
    """
    user_id = message.from_user.id if message.from_user else None
    logging.info(f"Received /start command from user {user_id}")
    welcome_text = (
        "Привет!\nЯ CinemaBot и я могу помочь"
        "вам найти информацию о фильмах.\n\n"
        "Вот что я умею:\n"
        "- Просто отправьте мне название фильма, и я найду информацию о нем.\n"
        "- Команда /history покажет вашу историю поиска.\n"
        "- Команда /stats покажет статистику поиска фильмов.\n"
        "- Команда /help покажет это сообщение."
    )
    await message.answer(welcome_text)


async def send_help(message: types.Message) -> None:
    """
    Send a help message to the user.

    :param message: The message object.
    """
    user_id = message.from_user.id if message.from_user else None
    logging.info(f"Received /help command from user {user_id}")
    help_text = (
        "Я CinemaBot и я могу помочь вам найти информацию о фильмах.\n\n"
        "Вот что я умею:\n"
        "- Просто отправьте мне название фильма, и я найду информацию о нем.\n"
        "- Команда /history покажет вашу историю поиска.\n"
        "- Команда /stats покажет статистику поиска фильмов.\n"
        "- Команда /help покажет это сообщение."
    )
    await message.answer(help_text)


async def search_and_send_movie(message: types.Message) -> None:
    """
    Search for a movie and send the details to the user.

    :param message: The message object.
    """
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(ANONYMOUS_MESSAGE)
        return
    logging.info(f"Received search query '{message.text}' from user {user_id}")
    if message.text:
        movie_details = await search_movie(message.text)
    else:
        await message.answer("Извините, я не понял ваш запрос.")
        return
    if movie_details:
        await log_search(user_id, movie_details['title'])
        star_rating = get_star_rating(movie_details['rating'])
        kinopoisk_url = f"https://www.kinopoisk.ru/film/{movie_details['id']}/"
        response_text = (
            f"<b>Название</b>:"
            f'<a href="{kinopoisk_url}">{movie_details["title"]}</a>\n'
            f"<b>Рейтинг</b>: {star_rating} ({movie_details['rating']})\n"
            f"<b>Описание</b>: {movie_details['description']}"
        )

        half_response = ''
        if movie_details['review_title']:
            half_response += f"\n<b>Отзыв</b>: {movie_details['review_title']}"
        if movie_details['online_viewing_link']:
            half_response += ('\n<b>Смотреть онлайн</b>: <a href="' +
                              movie_details["online_viewing_link"] + '">' +
                              movie_details["online_viewing_title"] + '</a>')
        if movie_details['fact']:
            temp_response_text = response_text + \
                f"\n<b>Интересный факт</b>: {movie_details['fact']}" + \
                half_response
            if len(temp_response_text) < 4096:
                response_text = temp_response_text
            else:
                response_text += half_response
        else:
            response_text += half_response

        await message.answer_photo(photo=movie_details['poster'],
                                   caption=response_text, parse_mode="HTML")
        logging.info("Sent movie details for "
                     f"'{message.text}' to user {user_id}")
    else:
        await message.answer("Извините, я не смог найти "
                             "фильм по вашему запросу.")
        logging.info("No movie found for "
                     f"query '{message.text}' from user {user_id}")


async def show_history(message: types.Message) -> None:
    """
    Show the search history to the user.

    :param message: The message object.
    """
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(ANONYMOUS_MESSAGE)
        return
    logging.info(f"Received /history command from user {user_id}")
    history = await get_history(user_id)
    if history:
        history_text = "\n".join(
            [f"{item[0]} ({format_time_ago(item[1])})"
                for item in history])
        await message.answer(f"<b>Последние {len(history)} "
                             f"запросов</b>:\n{history_text}",
                             parse_mode="HTML")
    else:
        await message.answer("У вас нет истории поиска.")
        logging.info(f"No search history found for user {user_id}")


async def show_stats(message: types.Message) -> None:
    """
    Show the search statistics to the user.

    :param message: The message object.
    """
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(ANONYMOUS_MESSAGE)
        return
    logging.info(f"Received /stats command from user {user_id}")
    user_stats = await get_user_stats(user_id)
    global_stats = await get_global_stats()

    user_stats_text = "\n".join(
        [f"{item[0]}: {item[1]} поисков" for item in user_stats])
    global_stats_text = "\n".join(
        [f"{item[0]}: {item[1]} поисков" for item in global_stats])

    response_text = (
        f"<b>Топ {len(user_stats)} ваших запросов</b>:\n{user_stats_text}\n\n"
        f"<b>Топ {len(global_stats)
                  } запросов пользователей</b>:\n{global_stats_text}"
    )

    await message.answer(response_text, parse_mode="HTML")


def register_handlers(dp: Dispatcher) -> None:
    """
    Register the command handlers with the dispatcher.

    :param dp: The dispatcher object.
    """
    dp.message.register(send_welcome, Command(commands=["start"]))
    dp.message.register(send_help, Command(commands=["help"]))
    dp.message.register(show_history, Command(commands=["history"]))
    dp.message.register(show_stats, Command(commands=["stats"]))
    dp.message.register(search_and_send_movie, F.text)
    logging.info("Handlers registered.")
