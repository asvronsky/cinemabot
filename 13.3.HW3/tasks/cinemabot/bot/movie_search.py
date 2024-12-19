import aiohttp
import os
import logging

KP_KEY = os.environ['KP_KEY']

async def search_movie(query):
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?query={query}"
    headers = {
        "X-API-KEY": KP_KEY
    }
    logging.info(f"Searching for movie '{query}' with URL: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                data = await response.json()
            except Exception as e:
                logging.error(f"Failed to parse JSON response: {e}")
                data = None
            if data and 'docs' in data and len(data['docs']) > 0:
                movie = data['docs'][0]
                logging.info(f"Found movie '{movie['name']}' for query '{query}'")
                return {
                    "title": movie['name'],
                    "rating": movie['rating']['kp'],
                    "poster": movie['poster']['url']
                }
            else:
                logging.info(f"No movie found for query '{query}'")
                return None
