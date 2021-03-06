import logging
from datetime import datetime

from telegram.error import BadRequest

from telegram import ParseMode, TelegramError

from telegram_stuff.resources import main_keyboard, main_keyboard_admin, main_edit_keyboard, edit_dare_keyboard
from utils.globals import Globals

logging.basicConfig(
    format='%(asctime)s - {%(pathname)s} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

log = logging.getLogger(__name__)


START_DATE = datetime.now()


def send_message(update, context, text, keyboard=None, preview_off=False, markdown=True):
    try:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=text,
            parse_mode=ParseMode.MARKDOWN if markdown else None,
            reply_markup=keyboard,
            disable_web_page_preview=preview_off
        )
    except TelegramError:
        log.warning(f"Can't send a message to {update.effective_user.id}")
    except BadRequest:
        log.warning(f"Can't send a message to {update.effective_user.id}, chat not found")


def delete_callback_message(update, context):
    try:
        context.bot.delete_message(
            chat_id=update.effective_user.id,
            message_id=update.callback_query.message.message_id
        )
    except TelegramError:
        pass
    except AttributeError:
        pass


def delete_message(message_id, chat_id, context):
    try:
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except TelegramError:
        log.warning(f"The message with id {message_id} is too old to be deleted.")


def delete_last_bot_message(update, context):
    delete_message(
        update.message.message_id - 1,
        update.effective_user.id,
        context
    )


def delete_last_message(update, context):
    delete_message(
        update.message.message_id,
        update.effective_user.id,
        context
    )


# SHORTCUTS -------------------------------------------------------

def send_main_menu(update, context):
    send_message(
        update,
        context,
        text="Choose what you want to do",
        keyboard=main_keyboard_admin if update.effective_user.id in Globals.admins_list else main_keyboard
    )


def send_edit_menu(update, context):
    send_message(
        update,
        context,
        text=f"Welcome to the edit menu!\n\n"
             f"there are currently *{len(Globals.DARES.pool)} saved dares*\n\n"
             f"*{Globals.GAMES_PLAYED} games* have been played and *{Globals.DARES_COMPLETED} dares* "
             f"have been completed by a total of *{Globals.TOTAL_PLAYERS} players* since "
             f"*{START_DATE.day}/{START_DATE.month}/{START_DATE.year}*\n\n"
             f"what do you want to do?",
        keyboard=main_edit_keyboard
    )


def send_edit_dare_menu(update, context):
    string = f"dare editor:\n\n{context.chat_data['dare']}"
    send_message(
        update,
        context,
        text=string,
        keyboard=edit_dare_keyboard
    )
