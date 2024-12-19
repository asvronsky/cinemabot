import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.filters.command import Command
from aiogram import F
import aiohttp

bot = Bot(token=os.environ['BOT_TOKEN'])
dp = Dispatcher()

async def on_startup(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/help", description="Get help")
    ])


@dp.message(Command(commands=["start", "help"]))
async def send_welcome(message: types.Message):
    await message.answer("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message(F.text)
async def echo(message: types.Message):
    if message.text:
        await message.answer(message.text)


async def main():
    await on_startup(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
