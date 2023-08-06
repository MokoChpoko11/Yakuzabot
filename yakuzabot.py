# -*- coding: utf-8 -*-
# @YAKUZA_REF_BOT TELEGRAM
import telebot
from telebot import types
from yakuzacfg import TOKEN, emoji, MONGO_TOKEN
from requests import exceptions
from pymongo import MongoClient
from random import randint
from telebot.apihelper import ApiTelegramException
from telebot.types import ReplyKeyboardRemove
import asyncio
bot = telebot.TeleBot(TOKEN)

mongo = MongoClient(MONGO_TOKEN, port=27017)

telebot = mongo["TelegramBot"]
usrs = telebot["Users"]
admins = telebot["Admins"]
sponsors = telebot["Sponsors"]
out_req = telebot['Withdraw']
comp = telebot['Completed Withdraws']
settings = telebot['Settings']
bans = telebot['Bans']

@bot.message_handler(commands=["start"])
def start_command_handler(message):
    FOUND = True
    ref_st = message.text
    for p in usrs.find({}, {'tgid': 1}):
        if p['tgid'] == message.chat.id:
            FOUND = False
            break
    def mu(message):
        b = ["🐲 Баланс 🐲", "🎎 Заробити 🎎",
             "🍜 Замовити рекламу 🍜", "🌋 Правила 🌋",'📊 Статистика 📊']
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(b[0], b[1])
        markup.add(b[2], b[3])
        markup.add(b[4])
        bot.send_message(message.chat.id, "Оберіть пункт меню:", reply_markup=markup)
    if FOUND:
        def phone(message):
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True,one_time_keyboard=True)
            button_phone = types.KeyboardButton(text="☎ Надіслати номер телефону", request_contact=True)
            keyboard.add(button_phone)
            s = bot.send_message(message.chat.id, '📞 Для продовження поділіться своїм номером телефону\n\n▪️Це потрібно для підтвердження, що ви українець, номер відразу буде видалений, та в Базах Даних не зберігатиметься',
                                 reply_markup=keyboard)
            bot.register_next_step_handler(s, login)
        def login(message):
            try:
                if message.contact.first_name == message.chat.first_name:
                    if int(message.contact.phone_number[1:4]) == 380 or int(message.contact.phone_number[0:3]) == 380:
                        bot.send_message(message.chat.id, f"{emoji['yep']}", reply_markup=ReplyKeyboardRemove())
                        res = usrs.insert_one(
                            {'tgid': message.chat.id, 'bal': 0, 'ref': 0, 'pr': '', 'get': 0, 'out': 0,
                             'name': message.from_user.first_name,'sp':1,
                             'nick': bot.get_chat_member(message.chat.id, message.chat.id).user.username})
                        xs = settings.find_one({})
                        settings.update_one({},
                                            {"$set": {'day': xs['day'] + 1}})
                        ref_candidate=''
                        if " " in ref_st:
                            ref_candidate = ref_st.split()[1]
                        try:
                            ref_candidate = int(ref_candidate)
                            if message.chat.id != ref_candidate:
                                link = f"@{bot.get_chat_member(ref_candidate, ref_candidate).user.username}"
                                bot.send_message(message.chat.id, f'{emoji["inf"]} *Ви були запрошені {link}*',
                                                 parse_mode='Markdown')
                                xus = usrs.find_one({'tgid': ref_candidate})
                                refs = xus['ref']
                                usrs.update_one({'tgid': message.chat.id},
                                                {"$set": {'pr': ref_candidate}})
                                usrs.update_one({'tgid': ref_candidate},
                                                {"$set": {'ref': refs + 1}})
                                bot.send_message(ref_candidate,
                                                 f'*ℹ За Вашим посилання зараховано нового реферала - @{message.from_user.username}*',
                                                 parse_mode='Markdown')
                            else:
                                bot.send_message(message.chat.id, 'Неможна запрошувати самого себе :)')
                        except Exception:
                            mu(message)
                        check_ch(message)
                    else:
                        bot.send_message(message.chat.id, 'На жаль, ми працюємо лише з українськими номерами')
                else:
                    bot.send_message(message.chat.id, f'It`s forbidden to resend a contact {emoji["redcr"]}')
                    bans.insert_one({'tgid': int(message.chat.id)})
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, emoji['vosk'] + ' Натисніть на кнопку нижче')
                phone(message)

        phone(message)
        def check_ch(message):
            def ch(message):
                tr = True
                for i in sponsors.find({}, {'_id': 1, 'id': 1, 'nick': 1, 'sub': 1}):
                    try:
                        if i['id'] != 1 and i['id'] != 2 and i['id'] != 3 and i['id'] != 4 and i['id'] != 5 and i[
                            'id'] != 6 and i['id'] != 7 and i['id'] != 8 and i['id'] != 9 and i['id'] != 10:
                            st = bot.get_chat_member(i['id'], message.chat.id).status
                            if st == 'member' or st == 'creator' or st == 'administrator':
                                tr = True
                            else:
                                tr = False
                                return False
                                break
                    except Exception as e:
                        for k in admins.find({}, {'tgid': 1}):
                            try:
                                if str(e) == 'A request to the Telegram API was unsuccessful. Error code: 403. Description: Forbidden: bot is not a member of the channel chat':
                                    bot.send_message(k['tgid'],
                                                     f"*ERROR*\n\nReason: Бот не знаходиться в каналі/Бота було кікнуто\nID: `{i['id']}`",
                                                     parse_mode='Markdown')
                                elif str(
                                        e) == 'A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: chat not found':
                                    bot.send_message(k['tgid'],
                                                     f"*ADMIN ALLERT*\n\nReason: Невірний айді каналу\nID: `{i['id']}`",
                                                     parse_mode='Markdown')
                                else:
                                    bot.send_message(k['tgid'],
                                                     f"*ADMIN ALLERT*\n\nReason: {e}\nID: `{iа['id']}`",
                                                     parse_mode='Markdown')
                            except Exception:
                                pass
                        if message.chat.id == 5288413290 or message.chat.id == 871076127:
                            return True
                if tr:
                    for i in settings.find({}, {'sp': 1}):
                        sponsub = i['sp']
                        break
                    try:
                        xf = usrs.find_one({'tgid': message.chat.id})
                        sp = xf['sp']
                        if sp != sponsub:
                            usrs.update_one({'tgid': message.chat.id}, {"$set": {'sp': sponsub}})
                            return False
                        else:
                            return True
                    except Exception as e:
                        print(e)
                        usrs.update_one({'tgid': message.chat.id}, {"$set": {'sp': sponsub}})
                        return False
                FOUND = False
                xf = usrs.find_one({'tgid': message.chat.id})

                try:
                    if xf['tgid'] == message.chat.id:
                        FOUND = True
                except Exception:
                    FOUND = False

                isban = True
                for g in bans.find({}, {'tgid': 1}):
                    if g['tgid'] == message.chat.id:
                        isban = False
                        break
            if ch(message):
                try:
                    for l in usrs.find({}, {'tgid': 1, 'bal': 1, 'pr': 1, 'get': 1}):
                        if l['tgid'] == message.chat.id:
                            if l['get'] == 0:
                                for n in settings.find({}, {'ref': 1, 'sht': 1}):
                                    ref_rew = float(n['ref'])
                                    sht = float(n['sht'])
                                    break
                                usrs.update_one({'tgid': message.chat.id},
                                                {"$set": {'get': 1}})
                                xu = usrs.find_one({'tgid': l['pr']})
                                usrs.update_one({'tgid': int(l['pr'])}, {"$set": {'bal': round(xu['bal'] + ref_rew, 2)}})
                                bot.send_message(l['pr'],
                                                 f'🎉 Ваш реферал підписався на спонсорів, Вам нараховано {ref_rew} ₴ - @{message.from_user.username}')
                                mu(message)
                            break
                except Exception as e:
                    print(e)
            else:
                inline_k = types.InlineKeyboardMarkup()
                c = 1
                lastsp = settings.find_one({})['lastsp']
                for i in sponsors.find({}, {'nick': 1, 'id': 1}):
                    if i['nick'][len(i['nick']) - 3:len(i['nick'])] == 'bot' or i['nick'][
                                                                                len(i['nick']) - 3:len(
                                                                                    i['nick'])] == 'Bot':
                        inline_bt = types.InlineKeyboardButton(f'({c}) Бот (натисніть /start)', callback_data='vip',
                                                               url=f'https://t.me/{i["nick"]}')
                        inline_k.add(inline_bt)
                        c += 1
                    else:
                        if lastsp != i['id']:
                            inline_bt = types.InlineKeyboardButton(f'({c}) Канал', callback_data='vip',
                                                                   url=f'https://t.me/{i["nick"]}')
                        else:
                            inline_bt = types.InlineKeyboardButton(f'({c}) Канал 🆕', callback_data='vip',
                                                                   url=f'https://t.me/{i["nick"]}')
                        inline_k.add(inline_bt)
                        c += 1
                inline_bt = types.InlineKeyboardButton(f'{emoji["yep"]} Підписався', callback_data='sub')
                inline_k.add(inline_bt)
                bot.send_message(message.chat.id,
                                 f'*Для користування ботом необхідно бути підписаним на канали спонсорів:*',
                                 reply_markup=inline_k, parse_mode='Markdown')
    else:
        b = ["🐲 Баланс 🐲", "🎎 Заробити 🎎",
             "🍜 Замовити рекламу 🍜", "🌋 Правила 🌋", '📊 Статистика 📊']
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(b[0], b[1])
        markup.add(b[2], b[3])
        markup.add(b[4])
        bot.send_message(message.chat.id, f'{emoji["inf"]} *Головне меню*', reply_markup=markup,parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def start_command_handler(message):
    def mu(message):
        b = ["🐲 Баланс 🐲", "🎎 Заробити 🎎",
             "🍜 Замовити рекламу 🍜", "🌋 Правила 🌋", '📊 Статистика 📊']
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(b[0], b[1])
        markup.add(b[2], b[3])
        markup.add(b[4])
        bot.send_message(message.chat.id, "Оберіть пункт меню:", reply_markup=markup)

    def admink(message):
        def adding(message):
            if message.text == emoji['back'] + ' Назад':
                admin_panel(message)
            elif len(message.text) == 9 or len(message.text) == 10:
                try:
                    if isinstance(int(message.text), int):
                        tr = True
                        for i in admins.find({}, {'tgid': 1}):
                            if i['tgid'] == message.text:
                                bot.send_message(message.chat.id, 'Цей користувач вже є адміном!')
                                tr = False
                                break
                        if tr:
                            res = admins.insert_one({'tgid': int(message.text)})
                            bot.send_message(message.chat.id, 'Користувач є адміном ' + emoji['yep'])
                        admin_panel(message)
                except TypeError:
                    pass
        def add_admin(message):
            if message.text == emoji['back'] + ' Назад':
                admin_panel(message)
            else:
                try:
                    if isinstance(int(message.text), int):
                        admins.insert_one({'tgid': int(message.text)})
                        bot.send_message(message.chat.id,f'Успіх ✅')
                        admin_panel(message)
                except Exception as e:
                    print(e)
                    admin_panel(message)
        def del_admin(message):
            if message.text == emoji['back'] + ' Назад':
                admin_panel(message)
            else:
                try:
                    if isinstance(int(message.text), int):
                        tru = True
                        for i in admins.find({}, {'tgid': 1}):
                            if int(i['tgid']) == int(message.text):
                                admins.delete_one(i)
                                bot.send_message(message.chat.id, 'Успіх ' + emoji['yep'])
                                tru = False
                                break
                        if tru:
                            bot.send_message(message.chat.id, 'Цей користувач не є адміном!')
                        admin_panel(message)
                except Exception as e:
                    print(e)
                    admin_panel(message)
        def nick_sp(message, tgid):
            if message.text == emoji['back'] + ' Назад':
                admin_panel(message)
            else:
                res = sponsors.insert_one({'id': tgid, 'nick': message.text, 'sub': ['871076127']})
                for i in settings.find({}, {'sp': 1}):
                    sponsub = i['sp']
                    break
                numli=[1,2,3,4,5,6,7,8,9,10]
                if tgid in numli:
                    settings.update_one({'sp': sponsub}, {"$set": {'sp':sponsub+1}})
                settings.update_one({}, {"$set": {'lastsp':tgid}})
                bot.send_message(message.chat.id, 'Канал є спонсором ' + emoji['yep'])
                admin_panel(message)

        def add_sp(message):
            if message.text == emoji['back'] + ' Назад':
                admin_panel(message)
            else:
                try:
                    if isinstance(int(message.text), int):
                        tr = True
                        chid=int(message.text)
                        if str(chid)[0]!='-' and chid!=1 and chid!=2 and chid!=3 and chid!=4 and chid!=5 and chid!=6 and chid!=7 and chid!=8 and chid!=9 and chid!=10:
                            chid=int(f'-{chid}')
                        try:
                            for i in sponsors.find({}, {'id': 1}):
                                if int(i['id']) == chid:
                                    bot.send_message(message.chat.id, 'Цей канал вже є спонсором!')
                                    tr = False
                                    admin_panel(message)
                                    break
                        except Exception:
                            pass
                        if tr:
                            tgid = int(chid)
                            markup_add = types.ReplyKeyboardMarkup(resize_keyboard=True)
                            markup_add.add(emoji['back'] + ' Назад')
                            k = bot.send_message(message.chat.id, 'Введіть nickname каналу (без @)',
                                                 reply_markup=markup_add)
                            bot.register_next_step_handler(k, nick_sp, tgid)
                except Exception as e:
                    print(e)

        def del_sp(message):
            if message.text == emoji['back'] + ' Назад':
                admin_panel(message)
            else:
                try:
                    if isinstance(int(message.text), int):
                        tru = True
                        chid = int(message.text)
                        if str(chid)[0] != '-' and chid!=1 and chid!=2 and chid!=3 and chid!=4 and chid!=5 and chid!=6 and chid!=7 and chid!=8 and chid!=9 and chid!=10:
                            chid = int(f'-{chid}')
                        for i in sponsors.find({}, {'id': 1}):
                            if int(i['id']) == int(chid):
                                sponsors.delete_one(i)
                                bot.send_message(message.chat.id, 'Канал більше не є спонсором ' + emoji['yep'])
                                tru = False
                                # bot.send_message(871076127, 'del1')
                                break
                        if tru:
                            bot.send_message(message.chat.id, 'Цей канал не є спонсором!')
                        admin_panel(message)
                except Exception:
                    pass
        def bck(message):
            admin_panel(message)
        async def mail_end(message, txt):
            if message.text == 'ПІДТВЕРДИТИ':
                err = 0
                alus2 = 0
                bot.send_message(message.chat.id, emoji[
                    'inf'] + ' Розсилання розпочато\n\nНе користуйтесь ботом, поки не отримаєте повідомлення о закінченні')
                msgid=message.message_id+1
                for i in settings.find({}, {'day': 1}):
                    dayus = i['day']
                    break
                for i in usrs.find({}, {'tgid': 1}):
                    try:
                        bot.send_message(i['tgid'], txt,parse_mode='HTML')
                        alus2 += 1
                    except Exception:
                        err += 1
                bot.send_message(message.chat.id,
                                 f"{emoji['inf']} Розсилання завершено\n\n{emoji['yep']} Надіслано: {alus2}\n{emoji['redc']} Заблокували: {err}")
                admin_panel(message)
            elif message.text == emoji["back"] + " Назад":
                admin_panel(message)
            else:
                bot.send_message(message.chat.id, 'Відхилено')
                admin_panel(message)

        def asyncmail(message, txt):
            asyncio.run(mail_end(message, txt))
        def mailing(message):
            markup_add = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup_add.add(emoji['back'] + ' Назад')
            if message.text == emoji["back"] + " Назад":
                admin_panel(message)
            else:
                txt = str(message.text)
                k = bot.send_message(message.chat.id, 'Введіть `ПІДТВЕРДИТИ`, щоб продовжити розсилання',
                                     reply_markup=markup_add,parse_mode='Markdown')
                bot.register_next_step_handler(k, asyncmail, txt)
        def out_new(message):
            try:
                if isinstance(float(message.text), float):
                    for l in settings.find({}, {'out': 1}):
                        settings.update_one({'out': l['out']}, {"$set": {'out': float(message.text)}})
                        bot.send_message(message.chat.id, 'Успішно відновлено ' + emoji['yep'])
                        sett(message)
                        break
            except Exception:
                sett(message)

        def ref_new(message):
            try:
                if isinstance(float(message.text), float):
                    for l in settings.find({}, {'ref': 1}):
                        settings.update_one({'ref': l['ref']}, {"$set": {'ref': float(message.text)}})
                        bot.send_message(message.chat.id, 'Успішно відновлено ' + emoji['yep'])
                        sett(message)
                        break
            except Exception:
                sett(message)
        def shtraf_new(message):
            if message.text == emoji['back'] + ' Назад':
                admin_panel(message)
            try:
                if isinstance(float(message.text), float):
                    for l in settings.find({}, {'sht': 1}):
                        settings.update_one({'sht': l['sht']}, {"$set": {'sht': float(message.text)}})
                        bot.send_message(message.chat.id, 'Штраф успішно відновлено ' + emoji['yep'])
                        sett(message)
                        break
            except Exception:
                sett(message)
        def sett_ch(message):
            if message.text == emoji['back'] + ' Назад':
                admin_panel(message)
            elif message.text == 'Мін. вивід':
                k = bot.send_message(message.chat.id, 'Введіть нову мінімальну суму для виведення')
                bot.register_next_step_handler(k, out_new)
            elif message.text == 'Оплата за реф.':
                k = bot.send_message(message.chat.id, 'Введіть нову нагороду за реферала')
                bot.register_next_step_handler(k, ref_new)
            elif message.text == 'Штраф за відписку':
                markup_se = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup_se.add(emoji['back'] + ' Назад')
                for l in settings.find({}, {'sht': 1}):
                    sht = l['sht']
                    break
                k = bot.send_message(message.chat.id,
                                     f'Штраф за відписку: {sht} ₴\n\nВведіть новий штраф за відписку',
                                     reply_markup=markup_se)
                bot.register_next_step_handler(k, shtraf_new)
            else:
                bot.send_message(message.chat.id, 'Не розумію Вас ' + emoji['bor'])
                sett(message)

        def sett(message):
            markup_set = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup_set.add('Мін. вивід','Оплата за реф.')
            markup_set.add('Штраф за відписку')
            markup_set.add(emoji['back'] + ' Назад')
            k = bot.send_message(message.chat.id, 'Оберіть:', reply_markup=markup_set)
            bot.register_next_step_handler(k, sett_ch)
        markup_add = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup_add.add(emoji['back'] + ' Назад')

        def adding_bal(message, balan, tgid):
            try:
                if message.text == emoji['back'] + ' Назад':
                    admin_panel(message)
                elif isinstance(float(message.text), float):
                    usrs.update_one({'tgid': tgid}, {"$set": {'bal': balan + float(message.text)}})
                    bot.send_message(message.chat.id, 'Баланс поповнено ' + emoji['yep'])
                    bot.send_message(tgid, f'Ваш баланс поповнено на {message.text} ₴ {emoji["star"]}')
                    admin_panel(message)
                else:
                    admin_panel(message)
            except Exception as e:
                admin_panel(message)

        def add_bal(message):
            try:
                if message.text == emoji['back'] + ' Назад':
                    admin_panel(message)
                elif isinstance(int(message.text), int):
                    for u in usrs.find({}, {'tgid': 1, 'bal': 1}):
                        if u['tgid'] == int(message.text):
                            balan = float(u['bal'])
                            tgid = int(u['tgid'])
                            k = bot.send_message(message.chat.id,
                                                 f'{emoji["man"]} Користувач - <a href="tg://user?id={tgid}">USER</a>\n{emoji["monbag"]} Баланс - {balan} ₴\n\n{emoji["tri"]}Введіть сумму, яку хочете додати до баланса',
                                                 parse_mode="HTML", reply_markup=markup_add)
                            bot.register_next_step_handler(k, adding_bal, balan, tgid)
                            break
                else:
                    admin_panel(message)
            except Exception:
                bot.send_message(message.chat.id, 'Невірний TelegramID ' + emoji['red'])
                admin_panel(message)
        def searchus(message):
            if message.text == emoji["back"] + ' Назад':
                admin_panel(message)
            else:
                try:
                    tgid=int(message.text)
                    xf = usrs.find_one({'tgid': tgid})
                    if xf['tgid']==tgid:
                        inline_s = types.InlineKeyboardMarkup()
                        inline_b1 = types.InlineKeyboardButton('🔴Бан', callback_data=f'ban{int(tgid)}')
                        inline_b2 = types.InlineKeyboardButton('🟢Розбан', callback_data=f'unb{int(tgid)}')
                        inline_s.add(inline_b1, inline_b2)
                        bot.send_message(message.chat.id,f'<b>Користувач</b>\n\n<b>TelegramID:</b> <code>{xf["tgid"]}</code>\n<b>Username:</b> @{bot.get_chat_member(xf["tgid"], xf["tgid"]).user.username}\n<b>User link:</b> <a href="tg://user?id={xf["tgid"]}">link</a>\n<b>Invited by:</b> <code>{xf["pr"]}</code>\n<b>Balance:</b> <code>{xf["bal"]}</code>\n<b>Referals:</b> <code>{xf["ref"]}</code>\n<b>Withdraw:</b> <code>{xf["out"]}</code>',parse_mode='HTML',reply_markup=inline_s)
                    else:
                        bot.send_message(message.chat.id,f'Користувача не знайдено {emoji["redcr"]}')
                    admin_panel(message)
                except Exception:
                    bot.send_message(message.chat.id,f'{emoji["redcr"]} Невірний ID')
                    admin_panel(message)


        if message.text == emoji['fl'] + ' Виведення':
            approving_out_admin(message)
        elif message.text == emoji['green'] + ' Додати спонсора':
            k = bot.send_message(message.chat.id, 'Введіть TelegramID спонсора (каналу)', reply_markup=markup_add)
            bot.register_next_step_handler(k, add_sp)
        elif message.text == emoji['paper'] + ' Всі спонсори':
            txt = ''
            c = 1
            for i in sponsors.find({}, {'id': 1, 'nick': 1}):
                txt += f"{c}. <a href='https://t.me/{i['nick']}'>Channel №{c}</a>\nID = {i['id']}\n"
                c += 1
            try:
                k = bot.send_message(message.chat.id, txt, parse_mode='HTML')
            except Exception:
                k = bot.send_message(message.chat.id, 'empty', parse_mode='HTML')
            bot.register_next_step_handler(k, admink)
        elif message.text == emoji['red'] + ' Видалити спонсора':
            k = bot.send_message(message.chat.id, 'Введіть TelegramID спонсора (каналу)', reply_markup=markup_add)
            bot.register_next_step_handler(k, del_sp)
        elif message.text == emoji['green'] + ' Додати адміна':
            k = bot.send_message(message.chat.id, 'Введіть TelegramID адміна', reply_markup=markup_add)
            bot.register_next_step_handler(k, add_admin)
        elif message.text == emoji['paper'] + ' Всі адміни':
            txt = ''
            c = 1
            for i in admins.find({}, {'tgid': 1}):
                txt += f"{c}. @{bot.get_chat_member(i['tgid'], i['tgid']).user.username}\nTGID = <code>{i['tgid']}</code>\n"
                c += 1
            k = bot.send_message(message.chat.id, txt, parse_mode='HTML')
            bot.register_next_step_handler(k, admink)
        elif message.text == emoji['red'] + ' Видалити адміна':
            k = bot.send_message(message.chat.id, 'Введіть TelegramID адміна', reply_markup=markup_add)
            bot.register_next_step_handler(k, del_admin)
        elif message.text == emoji["mai"] + ' Розсилання':
            k = bot.send_message(message.chat.id, "Напишіть текст для розсилки користувачам\n\n`<b></b>` - *жирний*\n`<code></code>` -`copyable`\n`<a href='google.com'>text</a>` - Посилання",
                                 reply_markup=markup_add,parse_mode='Markdown')
            bot.register_next_step_handler(k, mailing)
        elif message.text == emoji['gear'] + ' Налаштування':
            sett(message)
        elif message.text == emoji['monbag'] + ' Баланс':
            markup_ad = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup_ad.add(emoji['back'] + ' Назад')
            k = bot.send_message(message.chat.id, 'Введіть TelegramID користувача', reply_markup=markup_ad)
            bot.register_next_step_handler(k, add_bal)
        elif message.text==emoji['monbag']+' Всі заявки':
            pr=0
            cnt=1
            txt=''
            try:
                for k in out_req.find({}, {"tgid": 1, 'Card': 1, 'Sum': 1}):
                    txt+=f'{cnt}.\nUser: <b>@{bot.get_chat_member(k["tgid"],k["tgid"]).user.username}</b>\nWallet: <code>{k["Card"]}</code>\nSum: <code>{k["Sum"]}</code>\n'
                    cnt+=1
                    pr+=k["Sum"]
            except Exception:
                txt=f'Заявок немає {emoji["yep"]}'
            k=bot.send_message(message.chat.id,f'{txt}\n\n{emoji["fl"]} <b>Загальна сума: {pr}</b>',parse_mode='HTML')
            bot.register_next_step_handler(k, admink)
        elif message.text=='🔍 Пошук':
            k=bot.send_message(message.chat.id,f'🔍 Для пошуку користувача введіть TelegramID:',reply_markup=markup_add)
            bot.register_next_step_handler(k,searchus)
        elif message.text == emoji['back'] + ' Головне меню':
            mu(message)
        else:
            bot.send_message(message.chat.id, 'Не розумію Вас ' + emoji['bor'])
            admin_panel(message)

    def admin_panel(message):
        markup_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup_admin.add(emoji['monbag']+' Всі заявки')
        markup_admin.add(emoji['fl'] + ' Виведення',emoji["mai"] + ' Розсилання',emoji['gear'] + ' Налаштування')
        markup_admin.add(emoji['monbag'] + ' Баланс','🔍 Пошук')
        markup_admin.add(emoji['green'] + ' Додати спонсора', emoji['paper'] + ' Всі спонсори',
                         emoji['red'] + ' Видалити спонсора')
        markup_admin.add(emoji['green'] + ' Додати адміна', emoji['paper'] + ' Всі адміни',
                         emoji['red'] + ' Видалити адміна')
        markup_admin.add(emoji['back'] + ' Головне меню')
        t = bot.send_message(message.chat.id, 'Оберіть пункт меню', reply_markup=markup_admin)
        bot.register_next_step_handler(t, admink)
    def choosing_admin(message):
        out_req_comp = telebot['Completed Withdraws']
        req = list(out_req.find({}, {"tgid": 1, 'Card': 1, 'Sum': 1, 'Refs': 1}))
        if message.text == emoji["yep"] + " Підтвердити":
            completed_req = {"tgid": req[0]["tgid"], 'Card': req[0]["Card"], 'Refs': req[0]['Refs'],
                             "Sum": req[0]["Sum"]}
            completed_req1 = {"tgid": req[0]["tgid"], 'Card': req[0]["Card"], "Sum": req[0]["Sum"]}
            out_req.delete_one(completed_req)
            res = out_req_comp.insert_one(completed_req1)
            bot.send_message(message.chat.id, "Запит підтверждено")
            for us in usrs.find({}, {'_id': 1, 'tgid': 1, "out": 1}):
                if us['tgid'] == req[0]['tgid']:
                    usrs.update_one({'tgid': us['tgid']}, {"$set": {'out': us['out'] + req[0]['Sum']}})
            bot.send_message(completed_req['tgid'],
                             f"🔔 Зроблено виплату в розмірі {req[0]['Sum']} ₴, на картку: {req[0]['Card']}")
            approving_out_admin(message)
        elif message.text == emoji['redc'] + " Відхилити":
            completed_req = {"tgid": req[0]["tgid"], 'Card': req[0]["Card"],
                             "Sum": req[0]["Sum"]}
            out_req.delete_one(completed_req)
            bot.send_message(message.chat.id, "Запит відхилено")
            for us in usrs.find({}, {'_id': 1, 'tgid': 1, "bal": 1, 'ref': 1}):
                if us['tgid'] == req[0]['tgid']:
                    usrs.update_one({'tgid': us['tgid']}, {"$set": {'bal': us['bal'] + req[0]['Sum']}})
            bot.send_message(completed_req['tgid'],
                             f"Ваш  запит відхилено :(\nМожливо, Ви надали хибну інформацію або порушили правила нашого бота\nДля більш детальної інформації звертайтесь до адміністратора")
            approving_out_admin(message)
        elif message.text == emoji['back'] + " Назад":
            admin_panel(message)

    def approving_out_admin(message):
        req = list(out_req.find({}, {"tgid": 1, 'Card': 1, 'Sum': 1, 'Refs': 1}))
        markup_ap = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup_ap.add(emoji["yep"] + ' Підтвердити', emoji['redc'] + " Відхилити", emoji["back"] + " Назад")

        def backm(message):
            if message.text == emoji["back"] + " Назад":
                admin_panel(message)

        try:
            if len(req) == 1:
                bot.send_message(message.chat.id, f"У вас 1 новий запит")
            elif len(req) > 1:
                bot.send_message(message.chat.id, f"У вас {len(req)} нових запитів")
            link = f'<a href="tg://user?id={req[0]["tgid"]}">USER</a>'
            name=bot.get_chat_member(req[0]["tgid"], req[0]["tgid"]).user.username
            req_txt = f'User ID: <code>{req[0]["tgid"]}</code>\nUser: {link}\n@{name}\nКартка: <code>{req[0]["Card"]}</code>\nЗапросив: <b>{req[0]["Refs"]}</b>\nСума: <code>{req[0]["Sum"]}</code>'
            s = bot.send_message(message.chat.id, req_txt, reply_markup=markup_ap, parse_mode='HTML')
            bot.register_next_step_handler(s, choosing_admin)
        except IndexError:
            bot.send_message(message.chat.id, "Запитів немає!")
            admin_panel(message)

    def ask_mon(message):
        if message.text == emoji['back'] + ' Назад':
            mu(message)
        elif len(str(message.text))==16:
            user_card = str(message.text)
            for us in usrs.find({}, {'tgid': 1, "bal": 1}):
                if us['tgid'] == message.chat.id:
                    for l in settings.find({}, {'out': 1}):
                        min_out = l['out']
                        break
                    user_bal = us['bal']
                    m = bot.send_message(message.chat.id,
                                         f'{emoji["vosk"]} Введіть суму ₴ яку хочете вивести\n\n [Від {min_out}₴]\n\n{emoji["dol"]} Ваш баланс {us["bal"]} ₴')
                    bot.register_next_step_handler(m, approving_out, user_card, user_bal)
                    break
        else:
            bot.send_message(message.chat.id, 'Ви ввели невірний формат ' + emoji['bor'])
            card(message)

    def approving_out(message, user_card, user_bal):
        try:
            if message.text == emoji['back'] + ' Назад':
                mu(message)
            elif isinstance(float(message.text), float):
                for i in settings.find({}, {'out': 1, 'ref': 1}):
                    min_out = float(i['out'])
                if user_bal >= float(message.text):
                    if float(message.text) >= min_out:
                        mb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                        mb.add(emoji['back'] + ' Головне меню')
                        for us in usrs.find({}, {'_id': 1, 'tgid': 1, "bal": 1, 'ref': 1}):
                            if us['tgid'] == message.chat.id:
                                suma = float(message.text)
                                usrs.update_one({'_id': us['_id']}, {"$set": {'bal': us['bal'] - suma}})
                                out_request = {'tgid': message.chat.id, 'Card': user_card, 'Refs': us['ref'],
                                               'Sum': suma}
                                res = out_req.insert_one(out_request)
                                break
                        p = bot.send_message(message.chat.id,
                                             'Ваша заявка успішно прийнята, та йде на обробку адміністраторам ' + emoji[
                                                 'party'], reply_markup=mb)
                        try:
                            bot.send_message(5288413290,f'{emoji["fl"]} +1 заявка на виплату')
                        except Exception:
                            pass
                        bot.register_next_step_handler(p, back)
                    else:
                        bot.send_message(message.chat.id,
                                         emoji['vosk'] + f' Мінімальна сума для виведення - {min_out} ₴')
                        mu(message)
                else:
                    bot.send_message(message.chat.id, 'Недостатньо коштів ' + emoji['bor'])
                    mu(message)
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, emoji['vosk'] + ' Невірні данні!')
            mu(message)

    def back(message):
        if message.text == emoji['back'] + ' Назад':
            mu(message)
        elif message.text == emoji['back'] + ' Головне меню':
            mu(message)
        else:
            bot.send_message(message.chat.id, 'Не розумію Вас ' + emoji['bor'])
            mu(message)

    def card(message):
        mb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        mb.add(emoji['back'] + ' Назад')
        for i in settings.find({}, {'out': 1, 'ref': 1}):
            min_out = float(i['out'])
            break
        xusc = usrs.find_one({'tgid': message.chat.id})
        balan = xusc['bal']
        if balan >= min_out:
            l = bot.send_message(message.chat.id, emoji[
                'card'] + f'*Введіть номер Вашої банківської картки 🇺🇦\n\n{emoji["redc"]} Приклад :\n\n4441114402211329*',
                                 reply_markup=mb,parse_mode="Markdown")
            bot.register_next_step_handler(l, ask_mon)
        else:
            bot.send_message(message.chat.id, 'Недостатньо коштів ' + emoji['bor'])
            mu(message)
    def prov(message):
        if message.text == emoji['back'] + ' Назад':
            mu(message)
        elif message.text == 'На картку ' + emoji["ua"]:
            card(message)
    def menu(message):
        def mu(message):
            b = ["🐲 Баланс 🐲", "🎎 Заробити 🎎",
                 "🍜 Замовити рекламу 🍜", "🌋 Правила 🌋", '📊 Статистика 📊']
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(b[0], b[1])
            markup.add(b[2], b[3])
            markup.add(b[4])
            bot.send_message(message.chat.id, "*Оберіть пункт меню:*", reply_markup=markup,parse_mode='Markdown')
        def ch(message):
            tr = True
            for i in sponsors.find({}, {'_id': 1, 'id': 1, 'nick': 1, 'sub': 1}):
                try:
                    if i['id'] != 1 and i['id']!=2 and i['id']!=3 and i['id']!=4 and i['id']!=5 and i['id']!=6 and i['id']!=7 and i['id']!=8 and i['id']!=9 and i['id']!=10:
                        st = bot.get_chat_member(i['id'], message.chat.id).status
                        if st == 'member' or st == 'creator' or st == 'administrator':
                            tr = True
                        else:
                            tr = False
                            return False
                            break
                except Exception as e:
                    for k in admins.find({}, {'tgid': 1}):
                        try:
                            if str(e) == 'A request to the Telegram API was unsuccessful. Error code: 403. Description: Forbidden: bot is not a member of the channel chat':
                                bot.send_message(k['tgid'],
                                                 f"*ERROR*\n\nReason: Бот не знаходиться в каналі/Бота було кікнуто\nID: `{i['id']}`",
                                                 parse_mode='Markdown')
                            elif str(e) == 'A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: chat not found':
                                bot.send_message(k['tgid'],
                                                 f"*ADMIN ALLERT*\n\nReason: Невірний айді каналу\nID: `{i['id']}`",
                                                 parse_mode='Markdown')
                            else:
                                bot.send_message(k['tgid'],
                                                 f"*ADMIN ALLERT*\n\nReason: {e}\nID: `{iа['id']}`",
                                                 parse_mode='Markdown')
                        except Exception:
                            pass
                    if message.chat.id == 5288413290 or message.chat.id == 871076127:
                        return True
            if tr:
                for i in settings.find({}, {'sp': 1}):
                    sponsub = i['sp']
                    break
                try:
                    xf = usrs.find_one({'tgid': message.chat.id})
                    sp=xf['sp']
                    if sp!=sponsub:
                        usrs.update_one({'tgid': message.chat.id}, {"$set": {'sp': sponsub}})
                        return False
                    else:
                        return True
                except Exception as e:
                    print(e)
                    usrs.update_one({'tgid': message.chat.id}, {"$set": {'sp':sponsub}})
                    return False

        FOUND = False
        xf = usrs.find_one({'tgid': message.chat.id})

        try:
            if xf['tgid'] == message.chat.id:
                FOUND = True
        except Exception:
            FOUND=False

        isban = True
        for g in bans.find({}, {'tgid': 1}):
            if g['tgid'] == message.chat.id:
                isban = False
                break
        if ch(message):
            try:
                for l in usrs.find({}, {'tgid': 1, 'bal': 1,'pr':1,'get':1}):
                    if l['tgid']==message.chat.id:
                        if l['get']==0:
                            for n in settings.find({}, {'ref': 1,'sht':1}):
                                ref_rew = float(n['ref'])
                                sht = float(n['sht'])
                                break
                            usrs.update_one({'tgid': message.chat.id},
                                            {"$set": {'get':1}})
                            xu = usrs.find_one({'tgid': l['pr']})
                            usrs.update_one({'tgid': int(l['pr'])}, {"$set": {'bal': round(xu['bal'] + sht,2)}})
                        break
            except Exception as e:
                print(e)
            if FOUND:
                if isban:
                    xus = usrs.find_one({'tgid': message.chat.id})
                    b = ["🐲 Баланс 🐲", "🎎 Заробити 🎎",
                         "🍜 Замовити рекламу 🍜", "🌋 Правила 🌋"]
                    if message.text == "🍜 Замовити рекламу 🍜":
                        xs = settings.find_one({})
                        inline_k = types.InlineKeyboardMarkup()
                        inline_bt = types.InlineKeyboardButton(f"💫 Зв'язатись",callback_data='vip', url=f'https://t.me/bodya_kulinish')
                        inline_k.add(inline_bt)
                        bot.send_message(message.chat.id,
                                             f'*🔰Стати спонсором Yakuza, для піару свого контенту\n\n\n🎎Ваш канал буде в спонсорах, який всі бачуть на початку\n\n🐉Розсилання вашого повідомлення в боті\n\n🍿Наші люди це суто UA аудиторія\n\n🎐Якщо зацікавило пишить в особисті, там все буде в подробицях.*',parse_mode='Markdown',reply_markup=inline_k)
                    elif message.text == '📊 Статистика 📊':
                        xs = settings.find_one({})
                        day=xs['day']
                        bot.send_message(message.chat.id,f'*📊 Статистика проєкта:*\n\n👨‍💻 Людей в проєкті: {day}\n🕐 Старт бота: XX.08.23',parse_mode='Markdown')
                    elif message.text=="🌋 Правила 🌋":
                        bot.send_message(message.chat.id,f'*❌ Заборонено користуватись буксом, створювати завдання на набір рефералів, взаємна підписка, мультиаккаунти і тому подібне - одразу бан!\n\n❌ Заборонено поширювати неправдиву інформацію "Бот платить 5-10 грн і т.д" - анулювання вашого балансу!\n\n✅ Бот суто лише для UA аудиторії!\n\n✅ Дозволено спамити по чатам/каналам про "бот, який Платить"*',parse_mode='Markdown')
                    elif message.text == "🐲 Баланс 🐲":
                        refs = xus['ref']
                        balance = xus['bal']
                        pr = xus['pr']
                        out = xus['out']
                        inline_k = types.InlineKeyboardMarkup()
                        inline_bt = types.InlineKeyboardButton(f"💸 Вивести кошти", callback_data='withdraw')
                        inline_k.add(inline_bt)
                        bot.send_message(message.chat.id,f"📱 Ім'я: <b>{message.from_user.first_name}</b>\n🆔 ID: <code>{message.chat.id}</code>\n\n💵 <b>Баланс:</b> {balance}₴\n\n👨‍👧‍👦<b>Запрошено:</b> {refs}\n🙋 <b>Вас привів:</b> {f'@{bot.get_chat_member(pr, pr).user.username}' if len(str(pr))>1 else 'ніхто'}\n〰️ 〰️ 〰️ 〰️ 〰️ 〰️ 〰️ 〰️ 〰️\n💳 <b>Виведено:</b> {out}₴",parse_mode='HTML',reply_markup=inline_k)
                    elif message.text=="🎎 Заробити 🎎":
                        xs = settings.find_one({})
                        usc=xs['day']
                        ref_rew = xs['ref']
                        bot.send_message(message.chat.id,f'*🌋Скопіюйте своє реферальне посилання, і поширюйте масово людям\n\n\n🍿За кожну людину вам буде начислено ₴ на ваш баланс\n\n\n💥Це реферальне посилання ваше і його треба скопіювати:\n\n👺 Реферальне посилання -\n\nhttps://t.me/Yakuza_ref_bot?start={message.chat.id}\n\n⚠️Заробляйте не вкладаючись, в боті\n\n✅За одного запрошеного друга Ви отримаєте* `{ref_rew}₴`',parse_mode='Markdown')
                    elif message.text == '/admin' or message.text == 'admin':
                        k = True
                        for i in admins.find({}, {'tgid': 1}):
                            if int(i['tgid']) == message.chat.id:
                                t = bot.send_message(message.chat.id, f'*Вітаю, @{bot.get_chat_member(message.chat.id, message.chat.id).user.username}!*',parse_mode='Markdown')
                                admin_panel(message)
                                k = False
                                break
                        if k:
                            bot.send_message(message.chat.id, 'Не розумію Вас ' + emoji['bor'])
                            mu(message)
                    else:
                        bot.send_message(message.chat.id, 'Не розумію Вас ' + emoji['bor'])
                        mu(message)
                else:
                    bot.send_message(message.chat.id, emoji['redc'] + ' Ви були заблоковані в боті')
            else:
                mu(message)
        else:
            try:
                for l in usrs.find({}, {'tgid': 1, 'bal': 1, 'pr': 1, 'get': 1}):
                    if l['tgid'] == message.chat.id:
                        if l['get'] == 1:
                            for k in settings.find({}, {'sht': 1}):
                                sht = k['sht']
                                break
                            usrs.update_one({'tgid': message.chat.id},
                                            {"$set": {'get': 0}})
                            xu = usrs.find_one({'tgid': l['pr']})
                            usrs.update_one({'tgid': l['pr']}, {"$set": {'bal': round(xu['bal'] - sht, 2)}})
                            bot.send_message(l['pr'],f'{emoji["inf"]} @{message.from_user.username} відписався від спонсорів, знято {sht} ₴')
                        break
            except Exception as e:
                pass
            inline_k = types.InlineKeyboardMarkup()
            c = 1
            lastsp=settings.find_one({})['lastsp']
            for i in sponsors.find({}, {'nick': 1,'id':1}):
                if i['nick'][len(i['nick']) - 3:len(i['nick'])] == 'bot' or i['nick'][
                                                                            len(i['nick']) - 3:len(
                                                                                i['nick'])] == 'Bot':
                    inline_bt = types.InlineKeyboardButton(f'({c}) Бот (натисніть /start)', callback_data='vip',
                                                           url=f'https://t.me/{i["nick"]}')
                    inline_k.add(inline_bt)
                    c += 1
                else:
                    if lastsp!=i['id']:
                        inline_bt = types.InlineKeyboardButton(f'({c}) Канал', callback_data='vip',
                                                               url=f'https://t.me/{i["nick"]}')
                    else:
                        inline_bt = types.InlineKeyboardButton(f'({c}) Канал 🆕', callback_data='vip',
                                                               url=f'https://t.me/{i["nick"]}')
                    inline_k.add(inline_bt)
                    c += 1
            inline_bt = types.InlineKeyboardButton(f'{emoji["yep"]} Підписався', callback_data='sub1')
            inline_k.add(inline_bt)
            bot.send_message(message.chat.id, f'{emoji["redcr"]}')
            bot.send_message(message.chat.id,
                             f'*Для користування ботом необхідно бути підписаним на канали спонсорів:*',
                             reply_markup=inline_k, parse_mode='Markdown')
    menu(message)



@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    global markup
    b = ["🐲 Баланс 🐲", "🎎 Заробити 🎎",
         "🍜 Замовити рекламу 🍜", "🌋 Правила 🌋", '📊 Статистика 📊']
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(b[0], b[1])
    markup.add(b[2], b[3])
    markup.add(b[4])
    def approving_out(call, user_card, user_bal):
        try:
            if call.text == emoji['back'] + ' Назад':
                bot.send_message(call.from_user.id, 'Головне меню', reply_markup=markup)
            elif isinstance(float(call.text), float):
                for i in settings.find({}, {'out': 1, 'ref': 1}):
                    min_out = float(i['out'])
                if user_bal >= float(call.text):
                    if float(call.text) >= min_out:
                        for us in usrs.find({}, {'_id': 1, 'tgid': 1, "bal": 1, 'ref': 1}):
                            if us['tgid'] == call.from_user.id:
                                suma = float(call.text)
                                usrs.update_one({'tgid': us['tgid']}, {"$set": {'bal': us['bal'] - suma}})
                                out_request = {'tgid': call.from_user.id, 'Card': user_card, 'Refs': us['ref'],
                                               'Sum': suma}
                                res = out_req.insert_one(out_request)
                                break
                        bot.send_message(call.from_user.id,
                                             'Ваша заявка успішно прийнята, та йде на обробку адміністраторам ' + emoji[
                                                 'party'], reply_markup=markup)
                        try:
                            bot.send_message(824982798,f'{emoji["fl"]} +1 заявка на виплату')
                        except Exception:
                            pass
                    else:
                        bot.send_message(call.from_user.id,
                                         emoji['vosk'] + f' Мінімальна сума для виведення - {min_out} ₴',reply_markup=markup)
                else:
                    bot.send_message(call.from_user.id, 'Недостатньо коштів ' + emoji['bor'],reply_markup=markup)
        except Exception as e:
            print(e)
            bot.send_message(call.from_user.id, emoji['vosk'] + ' Невірні данні!',reply_markup=markup)
    def ask_mon(call):
        if call.text == emoji['back'] + ' Назад':
            bot.send_message(call.from_user.id,'Головне меню',reply_markup=markup)
        elif len(str(call.text))==16:
            user_card = str(call.text)
            for us in usrs.find({}, {'tgid': 1, "bal": 1}):
                if us['tgid'] == call.from_user.id:
                    for l in settings.find({}, {'out': 1}):
                        min_out = l['out']
                        break
                    user_bal = us['bal']
                    m = bot.send_message(call.from_user.id,
                                         f'{emoji["vosk"]} Введіть суму ₴ яку хочете вивести\n\n [Від {min_out}₴]\n\n{emoji["dol"]} Ваш баланс {us["bal"]} ₴')
                    bot.register_next_step_handler(m, approving_out, user_card, user_bal)
                    break
        else:
            bot.send_message(message.chat.id, 'Невірний формат картки' + emoji['bor'],reply_markup=markup)
    if call.data=='withdraw':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        for i in settings.find({}, {'out': 1, 'ref': 1}):
            min_out = float(i['out'])
            break
        xusc = usrs.find_one({'tgid': call.from_user.id})
        balan = xusc['bal']
        mb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        mb.add(emoji['back'] + ' Назад')
        if balan >= min_out:
            l = bot.send_message(call.from_user.id, emoji[
                'card'] + f'*Введіть номер Вашої банківської картки 🇺🇦\n\n{emoji["redc"]} Приклад :\n\n5168755910833956*',
                                 reply_markup=mb, parse_mode="Markdown")
            bot.register_next_step_handler(l, ask_mon)
        else:
            bot.send_message(call.from_user.id, f'_Недостатньо коштів_\n\n*Мінімальна сума виведення:* {min_out}₴\n*Ваш баланс*: {balan}₴',parse_mode='Markdown',reply_markup=markup)
    elif call.data == 'sub':
        try:
            bot.delete_message(call.from_user.id, call.message.message_id)
        except Exception:
            bot.send_message(call.from_user.id, emoji["yep"])
        def check_ch(call):
            def ch(call):
                tr = True
                trsp = True
                for i in sponsors.find({}, {'_id': 1, 'id': 1, 'nick': 1, 'sub': 1}):
                    try:
                        if i['id'] != 1 and i['id'] != 2 and i['id'] != 3 and i['id'] != 4 and i['id'] != 5 and i['id']!=6 and i['id']!=7 and i['id']!=8 and i['id']!=9 and i['id']!=10:
                            st = bot.get_chat_member(i['id'], call.from_user.id).status
                            if st == 'member' or st == 'creator' or st == 'administrator':
                                tr = True
                            else:
                                tr = False
                                return False
                                break
                    except Exception as e:
                        bot.send_message(871076127, f"{e}\n\n{i['id']}")
                        if call.from_user.id == 871076127:
                            # bot.send_message(5288413290, e)
                            return True
                        else:
                            return False
                        break
                if tr:
                    return True
            if ch(call):
                for l in usrs.find({}, {'tgid': 1, 'bal': 1, 'pr': 1, 'get': 1, 'ref': 1}):
                    if l['tgid'] == call.from_user.id:
                        if l['get'] == 0:
                            try:
                                for n in settings.find({}, {'ref': 1}):
                                    ref_rew = float(n['ref'])
                                    break
                                usrs.update_one({'tgid': call.from_user.id},
                                                {"$set": {'get': 1}})
                                for u in usrs.find({}, {'tgid': 1, 'bal': 1, 'pr': 1, 'ref': 1}):
                                    if l['pr'] == u['tgid']:
                                        usrs.update_one({'tgid': l['pr']},
                                                        {"$set": {'ref': u['ref'] + 1,
                                                                  'bal': round(u['bal'] + ref_rew, 3)}})
                                        break
                                bot.send_message(l['pr'],
                                                 f'🎉 Вітаємо, У вас новий реферал, Вам нараховано {ref_rew} ₴ - @{call.from_user.username}')
                            except Exception as e:
                                print(e)
                        break
                b = ["🐲 Баланс 🐲", "🎎 Заробити 🎎",
                     "🍜 Замовити рекламу 🍜", "🌋 Правила 🌋", '📊 Статистика 📊']
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(b[0], b[1])
                markup.add(b[2], b[3])
                markup.add(b[4])
                bot.send_message(call.from_user.id, "Оберіть пункт меню:", reply_markup=markup)
            else:
                bot.answer_callback_query(call.id, "Ви підписалися не на всіх спонсорів ❗")
                inline_k = types.InlineKeyboardMarkup()
                c = 1
                lastsp = settings.find_one({})['lastsp']
                for i in sponsors.find({}, {'nick': 1, 'id': 1}):
                    if i['nick'][len(i['nick']) - 3:len(i['nick'])] == 'bot' or i['nick'][
                                                                                len(i['nick']) - 3:len(
                                                                                    i['nick'])] == 'Bot':
                        inline_bt = types.InlineKeyboardButton(f'({c}) Бот (натисніть /start)', callback_data='vip',
                                                               url=f'https://t.me/{i["nick"]}')
                        inline_k.add(inline_bt)
                        c += 1
                    else:
                        if lastsp != i['id']:
                            inline_bt = types.InlineKeyboardButton(f'({c}) Канал', callback_data='vip',
                                                                   url=f'https://t.me/{i["nick"]}')
                        else:
                            inline_bt = types.InlineKeyboardButton(f'({c}) Канал 🆕', callback_data='vip',
                                                                   url=f'https://t.me/{i["nick"]}')
                        inline_k.add(inline_bt)
                        c += 1
                inline_bt = types.InlineKeyboardButton(f'{emoji["yep"]} Підписався', callback_data='sub')
                inline_k.add(inline_bt)
                bot.send_message(call.from_user.id,
                                 f'*Для користування ботом необхідно бути підписаним на канали спонсорів:*',
                                 reply_markup=inline_k, parse_mode='Markdown')
                # bot.register_next_step_handler(o, check_ch)

        check_ch(call)
    elif call.data == 'sub1':
        try:
            bot.delete_message(call.from_user.id, call.message.message_id)
        except Exception:
            bot.send_message(call.from_user.id, emoji["yep"])

        def check_ch(call):
            def ch(call):
                tr = True
                trsp = True
                for i in sponsors.find({}, {'_id': 1, 'id': 1, 'nick': 1, 'sub': 1}):
                    try:
                        if i['id'] != 1 and i['id'] != 2 and i['id'] != 3 and i['id'] != 4 and i['id'] != 5 and i['id']!=6 and i['id']!=7 and i['id']!=8 and i['id']!=9 and i['id']!=10:
                            st = bot.get_chat_member(i['id'], call.from_user.id).status
                            if st == 'member' or st == 'creator' or st == 'administrator':
                                tr = True
                            else:
                                tr = False
                                return False
                                break
                    except Exception as e:
                        bot.send_message(871076127, f"{e}\n\n{i['id']}")
                        if call.from_user.id == 871076127:
                            # bot.send_message(5288413290, e)
                            return True
                        else:
                            return False
                        break
                if tr:
                    return True
            if ch(call):
                for l in usrs.find({}, {'tgid': 1, 'bal': 1, 'pr': 1, 'get': 1}):
                    if l['tgid'] == call.from_user.id:
                        if l['get'] == 0:
                            try:
                                for n in settings.find({}, {'ref': 1}):
                                    ref_rew = float(n['ref'])
                                    break
                                for k in settings.find({}, {'sht': 1}):
                                    sht = k['sht']
                                    break
                                usrs.update_one({'tgid': call.from_user.id},
                                                {"$set": {'get': 1}})
                                for u in usrs.find({}, {'tgid': 1, 'bal': 1, 'pr': 1, 'ref': 1}):
                                    if l['pr'] == u['tgid']:
                                        usrs.update_one({'tgid': l['pr']},{"$set": {'bal': round(u['bal'] + sht, 2)}})
                                        break
                                bot.send_message(l['pr'], emoji['inf'] + f' @{call.from_user.username} повернувся до бота, Вам повернуто {sht} ₴')
                            except Exception as e:
                                print(e)
                        break
                b = ["🐲 Баланс 🐲", "🎎 Заробити 🎎",
                     "🍜 Замовити рекламу 🍜", "🌋 Правила 🌋", '📊 Статистика 📊']
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(b[0], b[1])
                markup.add(b[2], b[3])
                markup.add(b[4])
                bot.send_message(call.from_user.id, "Оберіть пункт меню:", reply_markup=markup)
            else:
                bot.answer_callback_query(call.id, "Ви підписалися не на всіх спонсорів ❗")
                inline_k = types.InlineKeyboardMarkup()
                c = 1
                lastsp = settings.find_one({})['lastsp']
                for i in sponsors.find({}, {'nick': 1, 'id': 1}):
                    if i['nick'][len(i['nick']) - 3:len(i['nick'])] == 'bot' or i['nick'][
                                                                                len(i['nick']) - 3:len(
                                                                                    i['nick'])] == 'Bot':
                        inline_bt = types.InlineKeyboardButton(f'({c}) Бот (натисніть /start)', callback_data='vip',
                                                               url=f'https://t.me/{i["nick"]}')
                        inline_k.add(inline_bt)
                        c += 1
                    else:
                        if lastsp != i['id']:
                            inline_bt = types.InlineKeyboardButton(f'({c}) Канал', callback_data='vip',
                                                                   url=f'https://t.me/{i["nick"]}')
                        else:
                            inline_bt = types.InlineKeyboardButton(f'({c}) Канал 🆕', callback_data='vip',
                                                                   url=f'https://t.me/{i["nick"]}')
                        inline_k.add(inline_bt)
                        c += 1
                inline_bt = types.InlineKeyboardButton(f'{emoji["yep"]} Перевірити підписку', callback_data='sub')
                inline_k.add(inline_bt)
                # mu_check = types.ReplyKeyboardMarkup(resize_keyboard=True)
                # mu_check.add('Підписався ' + emoji['yep'])
                #o = bot.send_message(call.from_user.id, f'{emoji["redcr"]}')
                bot.send_message(call.from_user.id,
                                 f'*Для користування ботом необхідно бути підписаним на канали спонсорів:*',
                                 reply_markup=inline_k, parse_mode='Markdown')
                # bot.register_next_step_handler(o, check_ch)
        check_ch(call)
    call3 = str(call.data)[:3]
    if call3 == 'ban':
        result = call.data[3:]
        tr = False
        for i in bans.find({}, {'tgid': 1}):
            if i['tgid'] == int(result):
                tr = True
                break
        if tr:
            bot.send_message(call.from_user.id, 'Користувач вже в бані')
        else:
            bans.insert_one({'tgid': int(result)})
            bot.send_message(call.from_user.id, f'Користувача `{result}` заблоковано ✅', parse_mode='Markdown')
    elif call3 == 'unb':
        result = call.data[3:]
        tr = True
        for i in bans.find({}, {'tgid': 1}):
            if i['tgid'] == int(result):
                tr = False
                break
        if tr:
            bot.send_message(call.from_user.id, 'Користувач не знаходиться в бані')
        else:
            bans.delete_one({'tgid': int(result)})
            bot.send_message(call.from_user.id, f'Користувача `{result}` розблоковано ✅', parse_mode='Markdown')
# ==Launching the bot==
if __name__ == '__main__':
    while True:
        try:
            print('Telegram Bot is starting')
            bot.polling()
        except Exception as e:
            bot.send_message(871076127, str(e)+"\n\nrestarted")
            print('Network Issues with Telegram')
