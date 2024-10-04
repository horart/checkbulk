import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.types import BotCommand, FSInputFile
import pyzbar
import PIL.Image
import pyzbar.pyzbar
import config
import query
import dbio

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
async def main():
    asyncio.create_task(dbio.init())
    await bot.set_my_commands([
        BotCommand(command='report', description='Сформировать отчёт <отчёт>|[арг1]|[арг2]|...'),
        BotCommand(command='categories', description='Категории товаров'),
        BotCommand(command='newcat', description='Создать категорию. <имя>'),
        BotCommand(command='newprod', description='Добавить продукт в категорию. <имя_категории> <regex>'),
        BotCommand(command='excel', description='Выгрузить все покупки в xlsx'),
        BotCommand(command='create_synonym', description='Создать синоним магазина. <магазин>|<синоним>'),
        BotCommand(command='reports', description='Показать все шаблоны отчётов'),
        BotCommand(command='topcats', description='Показать все надкатегории'),
        BotCommand(command='newtopcat', description='Создать новую надкатегорию. <имя>'),
        BotCommand(command='addtotopcat', description='Добавить категорию в надкатегорию <надкатегория> <категория>'),
    ])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

@dp.message(F.photo)
async def process(msg):
    await msg.bot.download(file=msg.photo[-1].file_id, destination='tmp.jpeg')
    try:
        qr = pyzbar.pyzbar.decode(PIL.Image.open('tmp.jpeg'))[0].data.decode('utf-8')
    except:
        return await msg.reply('Не распознано')
    data = query.query(qr)
    await dbio.write(*data, msg.from_user.id)
    await msg.reply(query.pretty_print(*data))
    
@dp.message(Command('report'))
async def report(msg, command: CommandObject=None):
    arg = command.args.split('|')
    data = await dbio.report(arg[0], msg.from_user.id, *arg[1:])
    await msg.reply(dbio.pretty_print(*data))

@dp.message(Command('newcat'))
async def new_cat(msg, command: CommandObject=None):
    if not command.args or len(command.args.split(' ')) > 1:
        return await msg.reply('Синтаксис: /newcat <имя>')
    await dbio.new_category(command.args, msg.from_user.id)
    await msg.reply('Создано!')

@dp.message(Command('newprod'))
async def new_prod(msg, command: CommandObject=None):
    if not command.args or len(command.args.split(' ')) != 2:
        return await msg.reply('Синтаксис: /newprod <имя_категории> <regex>')
    await dbio.new_product(*command.args.split(' '), msg.from_user.id)
    await msg.reply('Создано!')

@dp.message(Command('categories'))
async def ls_cats(msg, command: CommandObject=None):
    res = await dbio.ls_categories(msg.from_user.id)
    s = ''
    for i in res:
        s += (i[0] + ': ' + i[1]) + '\n'
    await msg.reply(s)

@dp.message(Command('excel'))
async def excel(msg, command: CommandObject=None):
    res = await dbio.get_user_records(msg.from_user.id)
    dbio.write_excel(res)
    await msg.reply_document(FSInputFile('report.xlsx'))

@dp.message(Command('create_synonym'))
async def new_syn(msg, command: CommandObject=None):
    if not command.args or len(command.args.split('|')) != 2:
        return await msg.reply('Синтаксис: /create_synonym <магазин>|<синоним>')
    await dbio.new_synonym(*command.args.split('|'), msg.from_user.id)
    await msg.reply('Создано!')

@dp.message(Command('reports'))
async def ls_rep(msg, command):
    await msg.reply(dbio.pretty_print(await dbio.ls_reports(msg.from_user.id)))

@dp.message(Command('topcats'))
async def ls_topcats(msg, command):
    res = await dbio.ls_top_categories(msg.from_user.id)
    s = ''
    for i in res:
        s += (i[0] + ': ' + i[1]) + '\n'
    await msg.reply(s)

@dp.message(Command('newtopcat'))
async def new_topcat(msg, command):
    if not command.args or len(command.args.split(' ')) > 1:
        return await msg.reply('Синтаксис: /newtopcat <имя>')
    await dbio.new_top_category(command.args, msg.from_user.id)
    await msg.reply('Создано!')

@dp.message(Command('addtotopcat'))
async def add_to_topcat(msg, command):
    if not command.args or len(command.args.split(' ')) != 2:
        return await msg.reply('Синтаксис: /newtopcat <имя надкатегории> <имя категории>')
    if await dbio.include_in_top_category(*command.args.split(' '), msg.from_user.id):
        return await msg.reply('Ошибка!')
    await msg.reply('Создано!')

if __name__ == "__main__":
    asyncio.run(main())



