import asyncio
import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import S

# ── Time conversion ──────────────────────────────────────────────────────────
def convert_time(duration_seconds: int) -> str:
    periods = [
        ('Year',   60 * 60 * 24 * 365),
        ('Month',  60 * 60 * 24 * 30),
        ('Day',    60 * 60 * 24),
        ('Hour',   60 * 60),
        ('Minute', 60),
        ('Second', 1),
    ]
    parts = []
    for name, secs in periods:
        if duration_seconds >= secs:
            n = duration_seconds // secs
            duration_seconds %= secs
            parts.append(f"{n} {name}{'s' if n > 1 else ''}")

    if not parts:
        return stylish_text("0 Seconds")
    if len(parts) == 1:
        return stylish_text(parts[0])
    return stylish_text(', '.join(parts[:-1]) + ' and ' + parts[-1])

DEL_MSG = S(
    "<blockquote>‼️ HEADS UP — READ BEFORE DOWNLOADING</blockquote>\n\n"
    "<blockquote>⏳ This file will be removed in <a href=\"https://t.me/{username}\">{time}</a></blockquote>\n"
    "<blockquote>(Copyright policy enforcement)</blockquote>\n\n"
    "<blockquote>📌 Forward this file to Saved Messages or another chat, then download from there.</blockquote>\n\n"
    "‣ Updates: <a href='https://t.me/Anime_Ocean_Official'>Animes Ocean</a>\n"
    "‣ Support: <a href='https://t.me/OceanXBotz'>OceanXBotz</a>"
)


async def auto_del_notification(bot_username, msg, delay_time, transfer):
    temp = await msg.reply_text(
        DEL_MSG.format(username=bot_username, time=convert_time(delay_time)),
        disable_web_page_preview=True
    )

    await asyncio.sleep(delay_time)

    try:
        if transfer:
            try:
                name = S("♻️ Tap Here")
                link = f"https://t.me/{bot_username}?start={transfer}"
                button = [[
                    InlineKeyboardButton(text=name, url=link),
                    InlineKeyboardButton(text=S("Dismiss ✖️"), callback_data="close")
                ]]
                await temp.edit_text(
                    text=S(
                        f"<b>Previous files have been removed. 🗑\n\n"
                        f"<blockquote>To retrieve the files again, tap the "
                        f"[<a href={link}>{name}</a>] button below, or close this message.</blockquote></b>"
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                    disable_web_page_preview=True
                )
            except Exception as e:
                await temp.edit_text(S("<b><blockquote>Previous message has been removed. 🗑</blockquote></b>"))
                print(f"Error while editing delete message: {e}")
        else:
            await temp.edit_text(S("<b><blockquote>Previous message has been removed. 🗑</blockquote></b>"))

    except Exception as e:
        print(f"Error while editing delete message: {e}")
        await temp.edit_text(S("<b><blockquote>Previous message has been removed. 🗑</blockquote></b>"))

    try:
        await msg.delete()
    except Exception as e:
        print(f"Error in auto_del_notification(): {e}")


async def delete_message(msg, delay_time):
    await asyncio.sleep(delay_time)
    try:
        await msg.delete()
    except Exception as e:
        print(f"Error in delete_message(): {e}")