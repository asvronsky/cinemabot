import asyncio
import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from bot.handlers import register_handlers  # Assuming you have a handlers.py file to register handlers
from bot.database import init_db  # Import the init_db function

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set logging level to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("cinemabot.log")  # Log to file
    ]
)

async def on_startup(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/help", description="Get help"),
        BotCommand(command="/history", description="Show search history"),
        BotCommand(command="/stats", description="Show search statistics")
    ])
    await init_db()  # Initialize the database
    logging.info("Bot started and commands set.")

async def main():
    bot = Bot(token=os.environ['BOT_TOKEN'])
    dp = Dispatcher()

    register_handlers(dp)  # Register handlers from handlers.py

    await on_startup(bot)
    logging.info("Starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.info("Starting bot...")
    asyncio.run(main())