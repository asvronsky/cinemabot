import sqlite3
import logging
from typing import List, Tuple


async def init_db() -> None:
    """
    Initialize the database by creating necessary tables if they do not exist.
    """
    conn = sqlite3.connect("cinemabot.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS search_history (
                        user_id INTEGER,
                        movie_title TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                      )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS movie_stats (
                        movie_title TEXT UNIQUE,
                        search_count INTEGER,
                        UNIQUE(movie_title)
                      )"""
    )
    conn.commit()
    conn.close()
    logging.info("Database initialized.")


async def log_search(user_id: int, movie_title: str) -> None:
    """
    Log a search query to the database.

    :param user_id: The ID of the user making the search.
    :param movie_title: The title of the movie being searched.
    """
    conn = sqlite3.connect("cinemabot.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO search_history (user_id, movie_title) VALUES (?, ?)",
        (user_id, movie_title),
    )
    cursor.execute(
        "INSERT INTO movie_stats (movie_title, search_count) VALUES (?, 1) "
        "ON CONFLICT(movie_title) DO UPDATE  "
        "SET search_count = search_count + 1",
        (movie_title,),
    )
    conn.commit()
    conn.close()
    logging.info(f"Logged search for user {user_id}: '{movie_title}'")


async def get_history(user_id: int) -> List[Tuple[str, str]]:
    """
    Retrieve the search history for a specific user.

    :param user_id: The ID of the user whose search history is being retrieved.
    :return: A list of tuples containing movie titles and timestamps.
    """
    conn = sqlite3.connect("cinemabot.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT movie_title, timestamp FROM search_history "
        "WHERE user_id = ? ORDER BY timestamp DESC LIMIT 15",
        (user_id,),
    )
    history = cursor.fetchall()
    conn.close()
    logging.info(f"Retrieved search history for user {user_id}")
    return history


async def get_user_stats(user_id: int) -> List[Tuple[str, int]]:
    """
    Retrieve the search statistics for a specific user.

    :param user_id: The ID of the user.
    :return: A list of tuples containing movie titles and search counts.
    """
    conn = sqlite3.connect("cinemabot.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT movie_title, COUNT(*) as count FROM search_history "
        "WHERE user_id = ? GROUP BY movie_title ORDER BY count DESC LIMIT 15",
        (user_id,),
    )
    user_stats = cursor.fetchall()
    conn.close()
    logging.info(f"Retrieved user search statistics for user {user_id}")
    return user_stats


async def get_global_stats() -> List[Tuple[str, int]]:
    """
    Retrieve the global search statistics.

    :return: A list of tuples containing movie titles and search counts.
    """
    conn = sqlite3.connect("cinemabot.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT movie_title, search_count FROM movie_stats "
        "ORDER BY search_count DESC LIMIT 5"
    )
    global_stats = cursor.fetchall()
    conn.close()
    logging.info("Retrieved global search statistics")
    return global_stats
