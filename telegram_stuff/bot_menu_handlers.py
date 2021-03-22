import logging
import traceback
from enum import Enum, auto

from telegram.ext import ConversationHandler

from telegram_stuff.functions import send_message, delete_callback_message, send_main_menu, send_edit_menu, send_edit_dare_menu
from telegram_stuff.resources import ingame_keyboard
from piccolo.game import PiccoloGame, PiccoloDare
from utils.globals import Globals


logging.basicConfig(
    format='%(asctime)s - {%(pathname)s} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

log = logging.getLogger(__name__)


class States(Enum):
    GET_PLAYERS = auto()
    IN_GAME = auto()
    MAIN_EDIT_MENU = auto()
    EDIT_DARE_MENU = auto()
    EDIT_DARE_ATTRIBUTE = auto()


def game_entrypoint_handler(update, context):
    delete_callback_message(update, context)
    send_message(
        update,
        context,
        text="Send the name of the players on different lines",
    )
    return States.GET_PLAYERS


def edit_entrypoint_handler(update, context):
    delete_callback_message(update, context)
    send_edit_menu(update, context)
    return States.MAIN_EDIT_MENU


def add_dare_handler(update, context):
    context.chat_data["dare"] = PiccoloDare()
    delete_callback_message(update, context)
    send_edit_dare_menu(update, context)
    return States.EDIT_DARE_MENU


def show_all_dares_handler(update, context):
    delete_callback_message(update, context)
    send_message(update, context, text=f"saved dares:\n\n{Globals.DARES}")
    send_edit_menu(update, context)
    return States.MAIN_EDIT_MENU


def edit_dare_menu_handler(update, context):
    cdata: str = update.callback_query.data
    delete_callback_message(update, context)
    if cdata == "save":
        Globals.DARES.add_dare(context.chat_data["dare"])
        Globals.DARES.save()
        send_edit_menu(update, context)
        return States.MAIN_EDIT_MENU
    else:
        context.chat_data["field"] = cdata
        field = cdata.replace("_", " ")
        send_message(update, context, text=f"write the new value for {field}")
        return States.EDIT_DARE_ATTRIBUTE


def edit_dare_attribute_handler(update, context):
    text: str = update.message.text
    field: str = context.chat_data["field"]
    dare: PiccoloDare = context.chat_data["dare"]
    field_type = type(dare.__dict__[field])
    if field_type == int:
        try:
            dare.__dict__[field] = int(text)
            send_edit_dare_menu(update, context)
            return States.EDIT_DARE_MENU
        except TypeError:
            send_message(update, context, text="Send a valid number")
    else:
        dare.__dict__[field] = text
        send_edit_dare_menu(update, context)
        return States.EDIT_DARE_MENU


def game_start_handler(update, context):
    text = update.message.text
    players = text.split("\n")
    game: PiccoloGame = PiccoloGame(
        Globals.DARES.pool,
        players,
        7
    )
    context.chat_data["turn"] = 0
    context.chat_data["game"] = game
    send_message(update, context, text="Click 'Next turn' to start!", keyboard=ingame_keyboard)
    return States.IN_GAME


def in_game_handler(update, context):
    delete_callback_message(update, context)
    game: PiccoloGame = context.chat_data["game"]
    messages = game.do_turn()
    if messages is not None:
        string = f"turn {context.chat_data['turn']}:\n\n"
        for message in messages:
            string += f"{message}\n\n"
        send_message(update, context, text=string, keyboard=ingame_keyboard)
        context.chat_data['turn'] += 1
        return States.IN_GAME
    else:
        send_message(update, context, text="Game ended")
        send_main_menu(update, context)
        return ConversationHandler.END


def start_command_handler(update, context):
    send_main_menu(update, context)


def about_command_handler(update, context):
    send_message(
        update,
        context,
        text="Bot built by @LordOmbro\n\n"
             "[\U00002615 Buy me a coffee!](https://www.paypal.com/donate?hosted_button_id=UBNSEND5E96H2)\n\n"
             "The code of the bot is open source and hosted [here](https://github.com/SudoOmbro/PiccoloBot)\n\n"
             "Contacts:\n"
             "[Github](https://github.com/SudoOmbro)\n"
             "[Instagram](https://www.instagram.com/_m_o_r_b_o_/)",
        preview_off=True
    )


def end_command_handler(update, context):
    send_message(update, context, text="Conversation ended")
    send_main_menu(update, context)
    return ConversationHandler.END


def error_handler(update, context):
    """Log Errors caused by Updates."""
    log.error(
        'with user: "%s (%s)"\nmessage: "%s"\ntraceback: %s',
        update.effective_user,
        update.effective_user.id,
        context.error,
        traceback.format_exc()
    )
