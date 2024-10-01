import asyncio
from aiogram import Bot, Dispatcher, F
import pyzbar
import PIL.Image
import pyzbar.pyzbar
import config
import query

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

@dp.message(F.photo)
async def process(msg):
    await msg.bot.download(file=msg.photo[-1].file_id, destination='tmp.jpeg')
    try:
        qr = pyzbar.pyzbar.decode(PIL.Image.open('tmp.jpeg'))[0].data.decode('utf-8')
    except:
        await msg.reply('Не распознано')
    query.save(qr)

if __name__ == "__main__":
    asyncio.run(main())