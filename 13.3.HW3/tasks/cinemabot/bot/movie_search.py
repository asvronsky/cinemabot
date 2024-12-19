import aiohttp
import os
import logging
from urllib.parse import quote_plus
import random
from typing import Tuple, Optional

KP_KEY = os.environ["KP_KEY"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
GOOGLE_CX = os.environ["GOOGLE_CX"]


async def get_movie_details(movie_id: int) -> Tuple[str, Optional[str]]:
    """
    Fetch movie details from Kinopoisk API.

    :param movie_id: The ID of the movie.
    :return: A tuple containing the description and a random fact.
    """
    url = f"https://api.kinopoisk.dev/v1.4/movie/{movie_id}"
    headers = {"X-API-KEY": KP_KEY}
    logging.info(f"Fetching details for movie ID '{movie_id}' with URL: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                data = await response.json()
                if "facts" in data:
                    facts = [
                        f["value"]
                        for f in data["facts"]
                        if not f.get("spoiler", False)
                    ]
                    fact = random.choice(facts) if facts else None
                else:
                    fact = None
                description = data.get(
                    "description", "Описание отсутствует"
                ).split("\n")[0]
                return description, fact
            except Exception as e:
                logging.error(
                    f"Failed to parse JSON response for details: {e}"
                )
                return "Описание отсутствует", None


async def get_random_review_title(movie_id: int) -> Optional[str]:
    """
    Fetch a random review title for a movie from Kinopoisk API.

    :param movie_id: The ID of the movie.
    :return: A random review title or None if no reviews are found.
    """
    url = (f"https://api.kinopoisk.dev/v1.4/review?page=1&limit=20"
           f"&selectFields=title&notNullFields=title&movieId={movie_id}")
    headers = {"X-API-KEY": KP_KEY}
    logging.info(f"Fetching reviews for movie ID '{movie_id}' with URL: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                data = await response.json()
                if "docs" in data and len(data["docs"]) > 0:
                    titles = [
                        review["title"]
                        for review in data["docs"]
                        if review["title"]
                    ]
                    return random.choice(titles) if titles else None
            except Exception as e:
                logging.error(
                    f"Failed to parse JSON response for reviews: {e}"
                )
                return None
    return None


async def get_online_viewing_link(query: str) \
        -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch an online viewing link for a movie using Google Custom Search API.

    :param query: The search query.
    :return: A tuple (link, title) of the first search result.
    """
    search_query = quote_plus(f"{query} смотреть онлайн")
    url = ("https://www.googleapis.com/customsearch/v1?"
           f"q={search_query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}")
    logging.info(f"Searching for online viewing link with URL: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                data = await response.json()
                if "items" in data and len(data["items"]) > 0:
                    return data["items"][0]["link"], data["items"][0]["title"]
            except Exception as e:
                logging.error(
                    "Failed to parse JSON response "
                    f"for online viewing link: {e}"
                )
                return None, None
    return None, None


async def search_movie(query: str) -> Optional[dict]:
    """
    Search for a movie and fetch its details.

    :param query: The search query.
    :return: A dictionary with movie details or None if movie not found.
    """
    encoded_query = quote_plus(query)
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?query={encoded_query}"
    headers = {"X-API-KEY": KP_KEY}
    logging.info(f"Searching for movie '{query}' with URL: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                data = await response.json()
            except Exception as e:
                logging.error(f"Failed to parse JSON response: {e}")
                data = None
            if data and "docs" in data and len(data["docs"]) > 0:
                movie = data["docs"][0]
                logging.info(
                    f"Found movie '{movie['name']}' "
                    "for query '{query}'"
                )
                description, fact = await get_movie_details(movie["id"])
                review_title = await get_random_review_title(movie["id"])
                online_viewing_result = await get_online_viewing_link(
                    movie["name"])
                online_viewing_link, online_viewing_title = \
                    online_viewing_result
                return {
                    "id": movie["id"],
                    "title": movie["name"],
                    "rating": movie["rating"]["kp"],
                    "poster": movie["poster"]["url"],
                    "description": description,
                    "fact": fact,
                    "review_title": review_title,
                    "online_viewing_link": online_viewing_link,
                    "online_viewing_title": online_viewing_title,
                }
            else:
                logging.info(f"No movie found for query '{query}'")
                return None
    return None
