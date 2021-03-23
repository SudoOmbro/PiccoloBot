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
    EDIT_DARE_GET_ID = auto()
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
    context.chat_data["new"] = True
    delete_callback_message(update, context)
    send_edit_dare_menu(update, context)
    return States.EDIT_DARE_MENU


def edit_dare_handler(update, context):
    delete_callback_message(update, context)
    send_message(update, context, text="type the id of the dare you want to edit")
    return States.EDIT_DARE_GET_ID


def edit_dare_get_dare_handler(update, context):
    text = update.message.text
    try:
        position = int(text)
        context.chat_data["dare"] = Globals.DARES.pool[position]
    except ValueError:
        send_message(update, context, text="invalid ID")
        send_edit_menu(update, context)
        return States.MAIN_EDIT_MENU
    except IndexError:
        send_message(update, context, text="out of bounds ID")
        send_edit_menu(update, context)
        return States.MAIN_EDIT_MENU
    context.chat_data["new"] = False
    delete_callback_message(update, context)
    send_edit_dare_menu(update, context)
    return States.EDIT_DARE_MENU


def show_all_dares_handler(update, context):
    delete_callback_message(update, context)
    pages = Globals.DARES.get_pages()
    for page in pages:
        send_message(update, context, text=page)
    send_edit_menu(update, context)
    return States.MAIN_EDIT_MENU


def edit_dare_menu_handler(update, context):
    cdata: str = update.callback_query.data
    delete_callback_message(update, context)
    if cdata == "save":
        if context.chat_data["new"]:
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
    # eh, this is pretty bad, but it works
    field_type = type(dare.__dict__[field])
    if field_type == int:
        try:
            dare.__dict__[field] = int(text)
        except TypeError:
            send_message(update, context, text="Send a valid number")
            return States.EDIT_DARE_ATTRIBUTE
    elif field == "strings":
        if text is not None:
            strings = text.replace(", ", ",").split(",")
            dare.__dict__[field] = strings
    else:
        dare.__dict__[field] = text
    send_edit_dare_menu(update, context)
    return States.EDIT_DARE_MENU


def edit_help_handler(update, context):
    delete_callback_message(update, context)
    send_message(
        update,
        context,
        text="*How do dares work?*\n"
             "dares have many attributes, here's an explanation of what each attribute does:\n"
             "1. *start text*: it's either just a prompt, like \"{1} does something to {2}\", "
             "or the message the bot sends at the start of a prompt that lasts multiple turns, like "
             "\"{1} does something until further notice\".\n"
             "2. *end text*: it's the prompt the bot sends at the expiration of a prompt that lasts multiple turns.\n"
             "3. *duration*: the prompt will last _duration_ turns, then expire with an _end text_ message.\n"
             "4. *wiggle*: if _duration_ isn't 0, the prompt will last "
             "between _duration_ and _duration + wiggle_ turns.\n"
             "5. *involved players*: the amount of players required to make this prompt work. For example"
             "\"{1} does something to {2}\" will require 2 involved players.\n"
             "6. *random strings*: pool of words from which a word will be chosen and randomly to replace the {r} tags "
             "during the generation of the prompt. The chosen words aren't consistent between turns.\n\n"
             "*tags*\n"
             "there are a few tags that you can use to add some flavour to your dares, here's how to use them:\n"
             "1. *player place tags ( {1}, {2}, ... )*: these tags show where player name go in the dare's prompt.\n"
             "2. *duration tag ( {d} )*: this tag will be replaced with the duration of the prompt.\n"
             "3. *letter tag ( {l} )*: this tag will be replace with a random capitalized letter.\n"
             "4. *random string tag ( {r} )*: this tag will be replace with a random string choosen "
             "from the _random strings_ pool\n\nThat's all! Have fun!"
    )
    send_edit_menu(update, context)
    return States.MAIN_EDIT_MENU


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
    return ConversationHandler.END
