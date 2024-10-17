from fdown_api import Fdown
from pydantic import BaseModel
from dotenv import dotenv_values
from os import remove
import typing as t
import telebot
import telebot.types as types


class BotConfig(BaseModel):
    token: str
    admin_id: t.Optional[int] = 0
    duration_limit: t.Optional[int] = 5 * 60
    timeout: t.Optional[int] = 20
    skip_pending: t.Optional[bool] = False
    long_polling_timeout: t.Optional[int] = 20


bot_config = BotConfig(**dotenv_values())

bot = telebot.TeleBot(bot_config.token)

help = (
    "Greetings %(user)s.\n"
    f"I can help you download Facebook videos under {bot_config.duration_limit} seconds. \n"
    "Send me any video url and I will download then send it over to you.\n\n"
    "Made with ❤️ by @AlphaBei from Kenya 🇰🇪"
)


def inline_delete_button(message: types.Message) -> types.InlineKeyboardButton:
    """Make delete button

    Args:
        message (types.Message): Message obj

    Returns:
        types.InlineKeyboardButton: Delete button.
    """
    button = types.InlineKeyboardButton(
        text="🗑️", callback_data=f"del:{message.chat.id}:{message.id}"
    )
    return button


def error_handler(help="An error occured and I couldn't complete that request!"):

    def main(func):
        def decorator(message: types.Message):
            try:
                return func(message)
            except Exception as e:
                markup = types.InlineKeyboardMarkup()
                markup.add(inline_delete_button(message))
                return bot.reply_to(message, help, reply_markup=markup)

        return decorator

    return main


@bot.message_handler(commands=["start", "help"])
def echo_help(msg: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(inline_delete_button(msg))
    markup.add(
        types.InlineKeyboardButton("Contact Developer", url="https://t.me/AlphaBei")
    )
    return bot.reply_to(
        msg, help % dict(user=msg.from_user.username), reply_markup=markup
    )


@bot.message_handler(regexp=r"https://.+\.facebook\.com.+?mibextid=\w{16}")
@error_handler()
def download_and_send_video(msg: types.Message):
    f = Fdown()
    video_links = f.get_links(msg.text)
    saved_to = f.download_video(
        video_links,
        progress_bar=False,
    )
    thumbnail = f.session.get(video_links.cover_photo).content
    markup = types.InlineKeyboardMarkup()
    markup.add(inline_delete_button(msg))

    bot.send_video(
        msg.chat.id,
        open(saved_to, "rb"),
        thumbnail=thumbnail,
        caption=video_links.title,
        reply_markup=markup,
    )
    remove(saved_to)
    return


@bot.message_handler(func=lambda msg: True)
def any_other_text(msg):
    markup = types.InlineKeyboardMarkup()
    markup.add(inline_delete_button(msg))
    bot.reply_to(
        msg,
        text="Kindly send a me a valid link to a Facebook video.",
        reply_markup=markup,
    )
    return


@bot.callback_query_handler(func=lambda call: call.data.startswith("del:"))
def delete_button_callback_handler(call: types.CallbackQuery):
    """Deletes a sent message"""
    _, chat_id, msg_id = call.data.split(":")
    try:
        bot.delete_message(chat_id, msg_id)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as e:
        try:
            bot.delete_message(call.message.chat.id, call.message.id)
        except:
            pass
        pass


if __name__ == "__main__":
    print("Infinity polling ...")
    bot.infinity_polling(
        timeout=bot_config.timeout,
        skip_pending=bot_config.skip_pending,
        long_polling_timeout=bot_config.long_polling_timeout,
    )
