from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = (
    "<b>🤖 𝗠𝘆 𝗡𝗮𝗺𝗲 :</b> "
    "<a href='https://t.me/AniIndexFilesbot'>AniIndex File Bot</a>\n"
    "<b>📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 :</b> "
    "<a href='https://t.me/AniIndex'>Ani Index</a>\n"
    "<b>🧑‍💻 𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 : </b> "
    "<a href='https://t.me/aniindexadminbot'>Someone</a>"
),
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Close", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass