from enum import Enum, auto

from telegram.ext import ConversationHandler

from telegram_stuff.functions import send_message, delete_callback_message, send_main_menu, send_edit_menu, send_edit_dare_menu
from telegram_stuff.resources import ingame_keyboard
from piccolo.game import PiccoloGame, PiccoloDare
from utils.globals import Globals


class States(Enum):
    GET_PLAYERS = auto()
    IN_GAME = auto()
    MAIN_EDIT_MENU = auto()
    EDIT_DARE_MENU = auto()
    EDIT_DARE_ATTRIBUTE = auto()


TEST_DARE_POOL = [

    PiccoloDare("{1} tocca il coccige di {2}, se si rifiuta beve 1 sorso.", 0, None, 2),
    PiccoloDare("{1} bacia a stampo {2}, se si rifiuta beve 2 sorsi.", 0, None, 2),
    PiccoloDare("{1} massaggia {2} fino a nuovo ordine", 4, "{1} puo' smettere di massaggiare {2}", 2),
    PiccoloDare("{1} e {2} leccano le orecchie a {3}, chi si rifuta beve 5 sorsi.", 0, None, 3),
    PiccoloDare("Mangiare un cucchiaio di unghie o dicapelli? Chi e' in minoranza beva 3 sorsi", 0, None, 0),
    PiccoloDare("{1} si toglie un indumento a sua scelta, se si rifiuta beve 3 sorsi.", 0, None, 1),
    PiccoloDare("{1} e {2} simulano una posizione sessuale a loro scelta. Se si rifitano bevono 4 sorsi.", 0, None, 2),
    PiccoloDare("{1} cerca nelle chat il primo messaggio con la parola scopare. Se si rifuta beve 3 sorsi.", 0, None, 2)

]


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
        Globals.DARES,
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


def end_command_handler(update, context):
    send_message(update, context, text="Conversation ended")
    send_main_menu(update, context)
    return ConversationHandler.END
