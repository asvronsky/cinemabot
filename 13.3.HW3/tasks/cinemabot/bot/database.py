import sqlite3
import asyncio
import logging

async def init_db():
    conn = sqlite3.connect('cinemabot.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS search_history (
                        user_id INTEGER,
                        query TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS movie_stats (
                        movie_title TEXT UNIQUE,
                        search_count INTEGER,
                        UNIQUE(movie_title)
                      )''')
    conn.commit()
    conn.close()
    logging.info("Database initialized.")

async def log_search(user_id, query):
    conn = sqlite3.connect('cinemabot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO search_history (user_id, query) VALUES (?, ?)', (user_id, query))
    cursor.execute('INSERT INTO movie_stats (movie_title, search_count) VALUES (?, 1) ON CONFLICT(movie_title) DO UPDATE SET search_count = search_count + 1', (query,))
    conn.commit()
    conn.close()
    logging.info(f"Logged search for user {user_id}: '{query}'")

async def get_history(user_id):
    conn = sqlite3.connect('cinemabot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT query, timestamp FROM search_history WHERE user_id = ?', (user_id,))
    history = cursor.fetchall()
    conn.close()
    logging.info(f"Retrieved search history for user {user_id}")
    return history

async def get_stats():
    conn = sqlite3.connect('cinemabot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT movie_title, search_count FROM movie_stats')
    stats = cursor.fetchall()
    conn.close()
    logging.info("Retrieved search statistics")
    return stats
