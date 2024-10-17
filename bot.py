from telebot import TeleBot
from fdown_api import Fdown
from pydantic import BaseModel
from dotenv import dotenv_values
from telebot.types import Message
from os import remove
import typing as t


class BotConfig(BaseModel):
    token: str
    admin_id: t.Optional[int] = 0
    duration_limit: t.Optional[int] = 5 * 60
    timeout: t.Optional[int] = 20
    skip_pending: t.Optional[bool] = False
    long_polling_timeout: t.Optional[int] = 20


bot_config = BotConfig(**dotenv_values())

bot = TeleBot(bot_config.token)

help = (
    "Greetings %(user)s.\n"
    f"I can help you download Facebook videos under {bot_config.duration_limit} seconds. \n"
    "Send me any video url and I will download and send it over to you."
)


@bot.message_handler(commands=["start", "help"])
def echo_help(msg: Message):
    return bot.reply_to(msg, help % dict(user=msg.from_user.username))


@bot.message_handler(regexp=r"https://.+\.facebook\.com.+?mibextid=\w{16}")
def download_and_send_video(msg: Message):
    f = Fdown()
    video_links = f.get_links(msg.text)
    saved_to = f.download_video(
        video_links,
        progress_bar=False,
    )
    thumbnail = f.session.get(video_links.cover_photo).contents
    bot.send_video(
        msg.chat.id,
        open(saved_to, "wb"),
        thumbnail=thumbnail,
        caption=video_links.title,
    )
    remove(saved_to)


if __name__ == "__main__":
    bot.infinity_polling(
        timeout=bot_config.timeout,
        skip_pending=bot_config.skip_pending,
        long_polling_timeout=bot_config.long_polling_timeout,
    )
