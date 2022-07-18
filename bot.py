import asyncio

from aiogram import Bot


async def main():
    bot = Bot("5404928995:AAF1WDSBfJQvVjQ5NcUXFxgUtrPY3")

    for i in range(20):
        await bot.send_message(73348621, "долбик")

    await bot.session.close()


asyncio.run(main())
