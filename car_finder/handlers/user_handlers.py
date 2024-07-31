from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboard import start_kb, send_application_kb, admin_application_kb, users_application_kb, driver_start_kb, dialogue_kb_driver, dialogue_kb_passenger
from services.services import (
    add_driver_id_username, add_driver_name, add_driver_surname, add_driver_car_number, 
    add_driver_car_model, add_driver_comment, check_admin_pass, add_or_update_admin, 
    check_admin_exists, get_application, get_active_admins, copy_user_to_drivers, 
    delete_user_from_applications, get_tg_id_by_username, insert_location, update_user,
    get_status_by_passenger_id, get_driver_id_by_passenger_id, update_status_by_passenger_id,
    get_active_passenger_by_driver_id, set_dialogues_inactive_by_driver_id, remove_driver_id_by_passenger_id,
    list_of_admins, delete_admin, list_of_drivers, delete_driver, list_of_users, 
    log_chat_start, log_chat_message, log_chat_end, get_log_filepath, get_active_applications, chat_logs
)

router = Router()
user_states = {}

@router.message(CommandStart())
async def process_start_command(message: Message):
    update_user(message.from_user.id, message.from_user.username, '0')
    path_to_photo = "car_finder/img/start_img.jpeg"
    caption = LEXICON_RU['/start']
    await message.answer_photo(
        types.FSInputFile(path=path_to_photo), 
        caption=caption, 
        reply_markup=start_kb(message.from_user.id)
    )
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

@router.message(Command(commands='admin'))
async def process_admin_command(message: Message):
    user_states[message.from_user.id] = 'admin_password_wait'
    await message.answer(text=LEXICON_RU['/admin'])

@router.message(Command(commands='panel'))
async def process_panel_command(message: Message):
    tg_id = message.from_user.id
    check = check_admin_exists(tg_id)
    if check:
        await message.answer(text=LEXICON_RU['/panel'], reply_markup=start_kb(message.from_user.id))
    else:
        await message.answer(text=LEXICON_RU['no_exist'], reply_markup=start_kb(message.from_user.id))

@router.message(Command(commands='applications'))
async def process_panel_command(message: Message):
    tg_id = message.from_user.id
    check = check_admin_exists(tg_id)
    if check:
        await message.answer(text=get_active_applications(), reply_markup=admin_application_kb)
    else:
        await message.answer(text=LEXICON_RU['no_exist'], reply_markup=start_kb(message.from_user.id))

@router.message(Command(commands='chat_log'))
async def process_panel_command(message: Message):
    tg_id = message.from_user.id
    check = check_admin_exists(tg_id)
    if check:
        await message.answer(text=chat_logs(), reply_markup=start_kb(message.from_user.id))
    else:
        await message.answer(text=LEXICON_RU['no_exist'], reply_markup=start_kb(message.from_user.id))

@router.message(Command(commands='del_admin'))
async def process_del_admin_command(message: Message):
    tg_id = message.from_user.id
    check = check_admin_exists(tg_id)
    if check:
        user_states[message.from_user.id] = 'del_admin'
        await message.answer(text=LEXICON_RU['del_admin'], reply_markup=start_kb(message.from_user.id))
    else:
        await message.answer(text=LEXICON_RU['no_exist'], reply_markup=start_kb(message.from_user.id))

@router.message(Command(commands='del_driver'))
async def process_del_driver_command(message: Message):
    tg_id = message.from_user.id
    check = check_admin_exists(tg_id)
    if check:
        user_states[message.from_user.id] = 'del_driver'
        await message.answer(text=LEXICON_RU['del_driver'], reply_markup=start_kb(message.from_user.id))
    else:
        await message.answer(text=LEXICON_RU['no_exist'], reply_markup=start_kb(message.from_user.id))

@router.message(Command(commands='admins'))
async def process_admin_command(message: Message):
    tg_id = message.from_user.id
    check = check_admin_exists(tg_id)
    text = '/del_admin - для удаления администратора\n\n' + list_of_admins()
    if check:
        await message.answer(text=text, reply_markup=start_kb(message.from_user.id))
    else:
        await message.answer(text=LEXICON_RU['no_exist'], reply_markup=start_kb(message.from_user.id))

@router.message(Command(commands='users'))
async def process_admin_command(message: Message):
    tg_id = message.from_user.id
    check = check_admin_exists(tg_id)
    text = 'Список пользователей:\n\n' + list_of_users()
    if check:
        await message.answer(text=text, reply_markup=start_kb(message.from_user.id))
    else:
        await message.answer(text=LEXICON_RU['no_exist'], reply_markup=start_kb(message.from_user.id))

@router.message(Command(commands='drivers'))
async def process_drivers_command(message: Message):
    tg_id = message.from_user.id
    check = check_admin_exists(tg_id)
    text = '/del_driver - для удаления водителя\n\n' + list_of_drivers()
    if check:
        await message.answer(text=text, reply_markup=start_kb(message.from_user.id))
    else:
        await message.answer(text=LEXICON_RU['no_exist'], reply_markup=start_kb(message.from_user.id))

@router.message(F.text == LEXICON_RU['Registration'])
async def process_reg_command(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username
    add_driver_id_username(tg_id, username)
    user_states[message.from_user.id] = 'reg_stage_1'
    await message.answer(text=LEXICON_RU['reg_stage_1'])

@router.message(F.text == LEXICON_RU['change_application'])
async def process_change_command(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username
    add_driver_id_username(tg_id, username)
    user_states[message.from_user.id] = 'reg_stage_1'
    await message.answer(text=LEXICON_RU['reg_stage_1'])

@router.message(F.text == LEXICON_RU['accept_application'])
async def process_change_command(message: Message):
    tg_id = message.from_user.id
    check = check_admin_exists(tg_id)
    if check:
        user_states[message.from_user.id] = 'admin_accept'
        await message.answer(text=LEXICON_RU['choose_username'], reply_markup=users_application_kb())
    else:
        await message.answer(text=LEXICON_RU['no_exist'], reply_markup=start_kb(message.from_user.id))

@router.message(F.text == LEXICON_RU['reject_application'])
async def process_change_command(message: Message):
    tg_id = message.from_user.id
    check = check_admin_exists(tg_id)
    if check:
        user_states[message.from_user.id] = 'admin_reject'
        await message.answer(text=LEXICON_RU['choose_username'], reply_markup=users_application_kb())
    else:
        await message.answer(text=LEXICON_RU['no_exist'], reply_markup=start_kb(message.from_user.id))

@router.message(F.text == LEXICON_RU['start_btn'])
async def process_check_live_location(message: Message):
    await message.answer(text=LEXICON_RU['live_location_guide'])

@router.message(F.text == LEXICON_RU['driver_start_button'])
async def process_check_live_location(message: Message):
    await message.answer(text=LEXICON_RU['live_location_guide'])

@router.message(F.location)
async def handle_first_live_location(message: Message):
    if message.location:
        tg_id = message.from_user.id
        latitude = message.location.latitude
        longitude = message.location.longitude
        insert_location(tg_id, latitude, longitude)
    await message.answer(text=LEXICON_RU['start_live_location'], reply_markup=start_kb(message.from_user.id))

@router.edited_message(F.location)
async def handle_updated_live_location(message: Message):
    if message.location:
        tg_id = message.from_user.id
        latitude = message.location.latitude
        longitude = message.location.longitude
        insert_location(tg_id, latitude, longitude)

@router.message(F.text == LEXICON_RU['send_application'])
async def process_reg_command(message: Message):
    admins = get_active_admins()
    application = get_application(message.from_user.id)
    bot = message.bot

    message_text = (
    "<b>Новая заявка:</b>\n\n"
    f"Telegram: @{application[1]}\n"
    f"Имя: {application[2]}\n"
    f"Фамилия: {application[3]}\n"
    f"Номер авто: {application[4]}\n"
    f"Модель авто: {application[5]}\n"
    f"Примечание: {application[6]}\n\n"
    )

    for admin in admins:
        admin_tg_id = admin[0]
        await bot.send_message(admin_tg_id, message_text, reply_markup=admin_application_kb)
    await message.answer(text=LEXICON_RU['sended_application'], reply_markup=start_kb(message.from_user.id))

@router.message(F.text == LEXICON_RU['stop_dialogue'])
async def process_stop_dialogue(message: Message):
    bot = message.bot
    passenger_id = get_active_passenger_by_driver_id(message.from_user.id)
    set_dialogues_inactive_by_driver_id(message.from_user.id)
    remove_driver_id_by_passenger_id(passenger_id)
    filepath = get_log_filepath(passenger_id, message.from_user.id)
    if filepath:
        log_chat_end(filepath, passenger_id, message.from_user.id)
    await bot.send_message(passenger_id, text=LEXICON_RU['dialogue_stopped_for_user'], reply_markup=start_kb(passenger_id))
    await message.answer(text=LEXICON_RU['dialogue_stopped'], reply_markup=start_kb(message.from_user.id))

@router.message(F.text == LEXICON_RU['stop_dialogue_passanger'])
async def process_stop_dialogue(message: Message):
    bot = message.bot
    driver_id = get_driver_id_by_passenger_id(message.from_user.id)
    set_dialogues_inactive_by_driver_id(driver_id)
    remove_driver_id_by_passenger_id(message.from_user.id)
    filepath = get_log_filepath(message.from_user.id, driver_id)
    if filepath:
        log_chat_end(filepath, message.from_user.id, driver_id)
    await bot.send_message(driver_id, text=LEXICON_RU['dialogue_stopped_for_driver'], reply_markup=start_kb(driver_id))
    await message.answer(text=LEXICON_RU['dialogue_stopped_by_passenger'], reply_markup=start_kb(message.from_user.id))

@router.message()
async def process_user_message(message: Message):
    if message.from_user.id in user_states and user_states[message.from_user.id] == 'reg_stage_1':
        add_driver_name(message.from_user.id, message.text)
        del user_states[message.from_user.id]
        user_states[message.from_user.id] = 'reg_stage_2'
        await message.answer(text=LEXICON_RU['reg_stage_2'])
    elif message.from_user.id in user_states and user_states[message.from_user.id] == 'reg_stage_2':
        add_driver_surname(message.from_user.id, message.text)
        del user_states[message.from_user.id]
        user_states[message.from_user.id] = 'reg_stage_3'
        await message.answer(text=LEXICON_RU['reg_stage_3'])
    elif message.from_user.id in user_states and user_states[message.from_user.id] == 'reg_stage_3':
        add_driver_car_number(message.from_user.id, message.text)
        del user_states[message.from_user.id]
        user_states[message.from_user.id] = 'reg_stage_4'
        await message.answer(text=LEXICON_RU['reg_stage_4'])
    elif message.from_user.id in user_states and user_states[message.from_user.id] == 'reg_stage_4':
        add_driver_car_model(message.from_user.id, message.text)
        del user_states[message.from_user.id]
        user_states[message.from_user.id] = 'reg_stage_5'
        await message.answer(text=LEXICON_RU['reg_stage_5'])
    elif message.from_user.id in user_states and user_states[message.from_user.id] == 'reg_stage_5':
        add_driver_comment(message.from_user.id, message.text)
        del user_states[message.from_user.id]
        application = get_application(message.from_user.id)
        message_text = (
            "Ваша заявка сформирована:\n\n"
            f"Telegram: @{application[1]}\n"
            f"Имя: {application[2]}\n"
            f"Фамилия: {application[3]}\n"
            f"Номер авто: {application[4]}\n"
            f"Модель авто: {application[5]}\n"
            f"Примечание: {application[6]}\n\n"
            "Если <b>ошиблись</b>, нажмите <b>Заново</b>\n"
            "Если <b>всё верно</b>, нажмите <b>Отправить</b>"
        )
        await message.answer(text=message_text, reply_markup=send_application_kb)
    elif message.from_user.id in user_states and user_states[message.from_user.id] == 'del_admin':
        delete_admin(message.text)
        del user_states[message.from_user.id]
        await message.answer(text=LEXICON_RU['user_deleted'], reply_markup=start_kb(message.from_user.id))
    elif message.from_user.id in user_states and user_states[message.from_user.id] == 'del_driver':
        text = delete_driver(message.text)
        del user_states[message.from_user.id]
        await message.answer(text=text, reply_markup=start_kb(message.from_user.id))
    elif message.from_user.id in user_states and user_states[message.from_user.id] == 'admin_password_wait':
        check = check_admin_pass(message.text)
        if check == 'poijhnugasdrfansjk':
            add_or_update_admin(message.from_user.id, message.from_user.username, 'active')
            del user_states[message.from_user.id]
            await message.answer(text=LEXICON_RU['pass_correct'], reply_markup=start_kb(message.from_user.id))
        else:
            del user_states[message.from_user.id]
            await message.answer(text=LEXICON_RU['pass_incorrect'], reply_markup=start_kb(message.from_user.id))
    elif message.from_user.id in user_states and user_states[message.from_user.id] == 'admin_accept':
        bot = message.bot
        del user_states[message.from_user.id]
        tg_id = get_tg_id_by_username(message.text)
        copy_user_to_drivers(message.text)
        delete_user_from_applications(message.text)
        await bot.send_message(tg_id, text=LEXICON_RU['application_accepted_user'], reply_markup=driver_start_kb(message.from_user.id))
        await message.answer(text=LEXICON_RU['application_accepted_admin'], reply_markup=admin_application_kb)
    elif message.from_user.id in user_states and user_states[message.from_user.id] == 'admin_reject':
        bot = message.bot
        del user_states[message.from_user.id]
        tg_id = get_tg_id_by_username(message.text)
        delete_user_from_applications(message.text)
        await bot.send_message(tg_id, text=LEXICON_RU['application_rejected_user'], reply_markup=start_kb(tg_id))
        await message.answer(text=LEXICON_RU['application_rejected_admin'], reply_markup=admin_application_kb)
    elif get_driver_id_by_passenger_id(message.from_user.id) is not None:
        bot = message.bot
        driver_id = get_driver_id_by_passenger_id(message.from_user.id)
        if get_status_by_passenger_id(message.from_user.id) in [None, 'inactive', 'wait']:
            update_status_by_passenger_id(message.from_user.id, 'active')
            filepath = log_chat_start(message.from_user.id, driver_id)
            text = LEXICON_RU['first_message'] + message.text
            admins = get_active_admins()
            for admin in admins:
                admin_tg_id = admin[0]
                message_text = 'Начался диалог'
                await bot.send_message(admin_tg_id, message_text, reply_markup=start_kb(admin_tg_id))
            await message.answer(text=LEXICON_RU['passenger_message'], reply_markup=dialogue_kb_passenger(driver_id, message.from_user.id))
            await bot.send_message(driver_id, text=text, reply_markup=dialogue_kb_driver(driver_id, message.from_user.id))
            log_chat_message(filepath, message.from_user.id, message.text)
        elif get_status_by_passenger_id(message.from_user.id) == 'active':
            text = LEXICON_RU['message'] + message.text
            filepath = get_log_filepath(message.from_user.id, driver_id)
            if filepath:
                log_chat_message(filepath, message.from_user.id, message.text)
            await bot.send_message(driver_id, text=text, reply_markup=dialogue_kb_driver(driver_id, message.from_user.id))
    elif get_active_passenger_by_driver_id(message.from_user.id) is not False:
        bot = message.bot
        passenger_id = get_active_passenger_by_driver_id(message.from_user.id)
        text = LEXICON_RU['message'] + message.text
        filepath = get_log_filepath(passenger_id, message.from_user.id)
        if filepath:
            print(f"Driver sending message, filepath: {filepath}")  # Debugging log
            log_chat_message(filepath, message.from_user.id, message.text)
        await bot.send_message(passenger_id, text=text, reply_markup=dialogue_kb_passenger(message.from_user.id, passenger_id))
    else:
        await message.answer(text=LEXICON_RU['unsupported_message'], reply_markup=start_kb(message.from_user.id))
