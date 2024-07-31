from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from lexicon.lexicon_ru import LEXICON_RU
from services.services import get_usernames, stop_sharing_location, is_recent_update, check_driver_exists

url = "http://56207.zetalink.ru"

def create_web_app_button(text, tg_id, role):
    location_allowed = is_recent_update(tg_id)
    if location_allowed == False:
        return KeyboardButton(text=text)
    return KeyboardButton(text=text, web_app={"url": f"{url}?tg_id={tg_id}&role={role}"})

def start_kb(tg_id):
    if check_driver_exists(tg_id):
        Driver_start_button = create_web_app_button(LEXICON_RU['start_btn'], tg_id, 'driver')
        return ReplyKeyboardMarkup(keyboard=[[Driver_start_button]], resize_keyboard=True)
    else:
        Find_button = create_web_app_button(LEXICON_RU['start_btn'], tg_id, 'passenger')
        return ReplyKeyboardMarkup(keyboard=[[Find_button]], resize_keyboard=True)

Send_button = KeyboardButton(text=LEXICON_RU['send_application'])
Change_button = KeyboardButton(text=LEXICON_RU['change_application'])
send_application_kb = ReplyKeyboardMarkup(keyboard=[[Send_button, Change_button]], resize_keyboard=True)

Acсept_button = KeyboardButton(text=LEXICON_RU['accept_application'])
Reject_button = KeyboardButton(text=LEXICON_RU['reject_application'])
Main_menu = KeyboardButton(text=LEXICON_RU['unsupported_message'])
admin_application_kb = ReplyKeyboardMarkup(keyboard=[[Acсept_button, Main_menu, Reject_button]], resize_keyboard=True)

def dialogue_kb_driver(driver_id, passenger_id):
    Stop_dialogue = KeyboardButton(text=LEXICON_RU['stop_dialogue'])
    Dialogue_map = KeyboardButton(text='Карта', web_app={"url": f"{url}/dialogue_map?driver_id={driver_id}&passenger_id={passenger_id}"})
    
    return ReplyKeyboardMarkup(keyboard=[[Stop_dialogue, Dialogue_map]], resize_keyboard=True)

def dialogue_kb_passenger(driver_id, passenger_id):
    Stop_dialogue_passenger = KeyboardButton(text=LEXICON_RU['stop_dialogue_passanger'])
    Dialogue_map = KeyboardButton(text='Карта', web_app={"url": f"{url}/dialogue_map?driver_id={driver_id}&passenger_id={passenger_id}"})
    
    return ReplyKeyboardMarkup(keyboard=[[Stop_dialogue_passenger, Dialogue_map]], resize_keyboard=True)

def driver_start_kb(tg_id):
    Driver_start_button = create_web_app_button(LEXICON_RU['driver_start_button'], tg_id, 'driver')
    return ReplyKeyboardMarkup(keyboard=[[Driver_start_button]], resize_keyboard=True)

def users_application_kb():
    usernames = get_usernames()
    user_buttons = []
    user_row = []
    for index, username in enumerate(usernames):
        button = KeyboardButton(text=username)
        user_row.append(button)
        if (index + 1) % 3 == 0 or index == len(usernames) - 1:
            user_buttons.append(user_row)
            user_row = []

    user_kb = ReplyKeyboardMarkup(keyboard=user_buttons, resize_keyboard=True)
    return user_kb
