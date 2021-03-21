import logging

from telegram.error import BadRequest

from telegram import ParseMode, TelegramError


logging.basicConfig(
    format='%(asctime)s - {%(pathname)s} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

log = logging.getLogger(__name__)


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
