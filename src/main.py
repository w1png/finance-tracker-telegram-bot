# Mockup of a plan:
# 
# Keyboard buttons:
# get my id
# if in family -> leave family
# if in family and is_family_creator -> invite a person by id | kick a person
# if not in family -> create a family | join a family
# 
# Database
# user -> user_id | family_id
# family -> family_id | user_list | creator_id 
# bills -> bill_id | family_id | user_id | price | message 

from datetime import datetime
from math import ceil
import sqlite3
from tokenize import String
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import user as usr
import markups as mk
import family as fam
import bill as b
import text_templates as tt
import state_handler as sh

conn = sqlite3.connect("data.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER, family_id INTEGER, username TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS families (family_id INTEGER, creator_id INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS invites (user_id INTEGER, family_id INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS bills (bill_id INTEGER, family_id INTEGER, user_id INGEGER, price REAL, message TEXT, date TEXT)")
conn.commit()


with open("token.txt", "r") as token_file:
    token = token_file.readline().rstrip()

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    user = usr.User(message.chat.id)
    await bot.send_message(
        chat_id=user.get_user_id(),
        text=tt.greeting,
        reply_markup=mk.get_markup_start(user),
    )

@dp.message_handler()
async def msg(message: types.Message):
    user = usr.User(message.chat.id)
    if message.text == tt.get_my_id:
        await bot.send_message(
            chat_id=user.get_user_id(),
            text=user.get_user_id(),
        )
    elif message.text == tt.change_my_name:
        await bot.send_message(
            chat_id=user.get_user_id(),
            text=f"Введите новое имя или нажмите на кнопку \"{tt.back}\"",
            reply_markup=mk.single_button(mk.btnCancelDelete)
        )
        await sh.changeName.name.set()
    elif message.text == tt.create_family:
        if not user.is_in_family():
            fam.create_family(user.get_user_id())
            await bot.send_message(
                chat_id=user.get_user_id(),
                text=f"Семья с ID {user.get_family().get_family_id()} была создана.",
                reply_markup=mk.get_markup_start(user)
            )
    elif message.text == tt.leave_family:
        if user.is_in_family():
            family = user.get_family()
            family.remove_user(user.get_user_id())
            await bot.send_message(
                chat_id=user.get_user_id(),
                text=f"Вы вышли из семьи.",
                reply_markup=mk.get_markup_start(user)
            )
    elif message.text == tt.my_invites:
        if not user.is_in_family():
            if user.get_invites():
                text = tt.my_invites
                markup = mk.get_markup_myInvites(user)
            else:
                text = tt.no_active_invites
                markup = types.InlineKeyboardMarkup()
        await bot.send_message(
            chat_id=user.get_user_id(),
            text=text,
            reply_markup=markup
        )
    elif message.text == tt.invite_to_family:
        await bot.send_message(
            chat_id=user.get_user_id(),
            text=f"Введите ID пользователя или нажмите на кнопку \"{tt.back}\".",
            reply_markup=mk.single_button(mk.btnCancelDelete)
        )
        await sh.InviteToFamily.invited_id.set()
    elif message.text == tt.kick_from_family:
        if user.is_in_family():
            if user.get_family().get_creator().get_user_id() == user.get_user_id():
                await bot.send_message(
                    chat_id=user.get_user_id(),
                    text=f"Выберите пользователя, которого хотите выгнать из семьи: ",
                    reply_markup=mk.get_markup_kickFromFamily(user.get_family())
                )
    elif message.text in [tt.family_bills_last_30_days, tt.my_bills_last_30_days]:
        if user.is_in_family():
            text = f"{tt.line_separator}\n"
            if message.text == tt.family_bills_last_30_days:
                bill_list = user.get_family().get_bills_30_days()
                own = False
            else:
                bill_list = user.get_family().get_bills_30_days(user.get_user_id())
                own = True

            markup = types.InlineKeyboardMarkup()
            if len(bill_list) > 30:
                markup = mk.get_markup_billsPage(pagenum=1, maxpages=ceil(len(bill_list) / 30), own=own)
                bill_list = bill_list[:30]
                
            
            for bill in bill_list[::-1]:
                text += f"{'{:.2f}'.format(bill.get_price())} руб. - \"{bill.get_message()}\"\nДобавлено {bill.get_user().get_name()} {datetime.strftime(bill.get_date(), '%d-%m-%y в %H:%M')}\n{tt.line_separator}\n"
            text += f"{tt.family_bills_last_30_days if message.text == tt.family_bills_last_30_days else tt.my_bills_last_30_days}: {'{:.2f}'.format(user.get_family().get_total_30_days(None if message.text == tt.family_bills_last_30_days else user.get_user_id()))}руб."
            await bot.send_message(
                chat_id=user.get_user_id(),
                text=text,
                reply_markup=markup
            )
    else:
        if user.is_in_family():
            try:
                price = float(message.text.split(" - ")[0])
                msg = message.text.split(" - ")[1]
                if len(msg) > 120:
                    text = f"Сообщение не может быть больше 120 символов!"
                else:
                    b.create_bill(user.get_family().get_family_id(), user.get_user_id(), price, msg)
                    text = f"Счет на {price}руб. был добавлен с сообщением \"{msg}\"."
            except:
                text = tt.error
        else:
            text = "Вступите в семью для добавления трат."
        await bot.send_message(
            chat_id=user.get_user_id(),
            text=text,
        )


@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery):
    user = usr.User(callback_query.message.chat.id)
    call_data = callback_query.data
    message_id = callback_query.message.message_id

    if call_data.startswith("acceptFamily"):
        if fam.family_exists(call_data[12:]):
            family = fam.Family(call_data[12:])
            if not user.is_in_family() and user.is_invited(family.get_family_id()):
                family.add_user(user.get_user_id())
                user.delete_invite(family.get_family_id())

                text = f"Вы вступили в семью с ID {user.get_family().get_family_id()}."
                markup = mk.get_markup_start(user)
        else:
            text = f"Семьи с ID {call_data[12:]} больше не существует."
            user.delete_invite(call_data[12:])
            markup = mk.single_button(mk.btnBackMyInvites)
        await bot.edit_message_text(
                chat_id=user.get_user_id(),
                message_id=message_id,
                text=text,
                reply_markup=markup
            )
    elif call_data == "myInvites":
        if not user.is_in_family():
            if user.get_invites():
                text = tt.my_invites
                markup = mk.get_markup_myInvites(user)
            else:
                text = tt.no_active_invites
                markup = types.InlineKeyboardMarkup()
            await bot.edit_message_text(
                chat_id=user.get_user_id(),
                message_id=message_id,
                text=text,
                reply_markup=markup
            )
    elif call_data.startswith("declineFamily"):
        family = fam.Family(call_data[13:])
        if not user.is_in_family() and user.is_invited(family.get_family_id()):
            user.delete_invite(family.get_family_id())
            if user.get_invites():
                text = tt.my_invites
                markup = mk.get_markup_myInvites(user)
            else:
                text = tt.no_active_invites
                markup = types.InlineKeyboardMarkup()
            await bot.edit_message_text(
                chat_id=user.get_user_id(),
                message_id=message_id,
                text=text,
                reply_markup=markup
            )
    elif call_data == "kickFromFamily":
        if user.is_in_family():
            if user.get_family().get_creator().get_user_id() == user.get_user_id():
                await bot.edit_message_text(
                    chat_id=user.get_user_id(),
                    message_id=message_id,
                    text=f"Выберите пользователя, которого хотите выгнать из семьи: ",
                    reply_markup=mk.get_markup_kickFromFamily(user.get_family())
                )
    elif call_data.startswith("kickFromFamily"):
        kicked_user = usr.User(call_data[14:])
        family = kicked_user.get_family()

        if user.get_user_id() == kicked_user.get_user_id():
            text = "Вы не можете выгнать самого себя!"
        elif user.is_in_family() and kicked_user.is_in_family():
            if kicked_user.get_family().get_creator().get_user_id() == user.get_user_id() and kicked_user.get_family().get_family_id() == user.get_family().get_family_id():
                    await bot.send_message(
                        chat_id=kicked_user.get_user_id(),
                        text=f"Вы были выгнаны из семьи с ID {family.get_family_id()}.",
                    )
                    text = f"Пользователь {kicked_user.get_name()} был выгнан из семьи."
                    family.remove_user(kicked_user.get_user_id())
        await bot.edit_message_text(
            chat_id=user.get_user_id(),
            message_id=message_id,
            text=text,
            reply_markup=mk.single_button(mk.btnBackKickFromFamily)
        )

    elif call_data.startswith("billsPage") or call_data.startswith("ownbillsPage"):
        if call_data.startswith("ownbillsPage"):
            pagenum = int(call_data[12:])
            bill_list = user.get_family().get_bills_30_days(user_id=user.get_user_id())
            own = True
        else:
            pagenum = int(call_data[9:])
            bill_list = user.get_family().get_bills_30_days()
            own = False
        bill_offset_start = 0 if pagenum == 1 else 30*(pagenum-1)
        maxpages = ceil(len(bill_list) / 30)
        bill_list = bill_list[bill_offset_start:bill_offset_start+30]

        text = ""
        for bill in bill_list[::-1]:
            text += f"{'{:.2f}'.format(bill.get_price())} руб. - \"{bill.get_message()}\"\nДобавлено {bill.get_user().get_name()} {datetime.strftime(bill.get_date(), '%d-%m-%y в %H:%M')}\n{tt.line_separator}\n"
        text += f"{tt.family_bills_last_30_days if not own else tt.my_bills_last_30_days}: {'{:.2f}'.format(user.get_family().get_total_30_days(None if not own else user.get_user_id()))}руб."
        
        await bot.edit_message_text(
            text=text,
            chat_id=user.get_user_id(),
            message_id=message_id,
            reply_markup=mk.get_markup_billsPage(pagenum, maxpages=maxpages, own=own)
        )


@dp.message_handler(state=sh.InviteToFamily.invited_id)
async def inviteToFamilySetInvitedID(message: types.Message, state: FSMContext):
    user = usr.User(message.chat.id)
    family = user.get_family()
    if usr.user_exists(message.text):
        invited_user = usr.User(message.text)
        if invited_user.is_in_family():
            text = f"Пользователь {invited_user.get_name()} уже находится в семье."
        elif invited_user.is_invited(family.get_family_id()):
            text = f"Пользователь {invited_user.get_name()} уже был приглашен в семью с ID {family.get_family_id()}."
        else:
            try:
                invited_user.create_invite(user.get_family().get_family_id())
                await bot.send_message(
                    chat_id=invited_user.get_user_id(),
                    text=f"Вы были приглашены в семью с ID {user.get_family().get_family_id()}.",
                    reply_markup=mk.single_button(mk.btnMyInvites)
                )
                text = f"Пользователь {invited_user.get_name()} был приглашен в семью с ID {user.get_family().get_family_id()}."
            except:
                text = tt.error
    else:
        text = f"Пользователя с ID {message.text} не существует."
    
    await bot.send_message(
        chat_id=user.get_user_id(),
        text=text
    )
    await state.finish()


@dp.message_handler(state=sh.changeName.name)
async def changeNameSetName(message: types.Message, state: FSMContext):
    user = usr.User(message.chat.id)
    user.set_name(message.text)
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Ваше имя было изменено на \"{message.text}\".",
    )
    await state.finish()

@dp.callback_query_handler(state='*')
async def cancelState(callback_query: types.CallbackQuery, state: FSMContext):
    user = usr.User(callback_query.message.chat.id)
    call_data = callback_query.data
    
    if call_data == "cancelDelete":
        try:
            await bot.delete_message(
                chat_id=user.get_user_id(),
                message_id=callback_query.message.message_id
            )
        except:
            pass # It's a shame I had to do this.
        await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


