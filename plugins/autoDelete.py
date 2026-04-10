# +++ Made By King [telegram username: @Shidoteshika1] +++

#from bot import Bot
import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from datetime import datetime, timedelta

#Time conversion for auto delete timer
def convert_time(duration_seconds: int) -> str:
    periods = [
        ('Yᴇᴀʀ', 60 * 60 * 24 * 365),
        ('Mᴏɴᴛʜ', 60 * 60 * 24 * 30),
        ('Dᴀʏ', 60 * 60 * 24),
        ('Hᴏᴜʀ', 60 * 60),
        ('Mɪɴᴜᴛᴇ', 60),
        ('Sᴇᴄᴏɴᴅ', 1)
    ]

    parts = []
    for period_name, period_seconds in periods:
        if duration_seconds >= period_seconds:
            num_periods = duration_seconds // period_seconds
            duration_seconds %= period_seconds
            parts.append(f"{num_periods} {period_name}{'s' if num_periods > 1 else ''}")

    if len(parts) == 0:
        return "0 Sᴇᴄᴏɴᴅ"
    elif len(parts) == 1:
        return parts[0]
    else:
        return ', '.join(parts[:-1]) +' ᴀɴᴅ '+ parts[-1]


#=====================================================================================##
#.........Auto Delete Functions.......#
#=====================================================================================##
DEL_MSG = """<blockquote>‼️ 𝗜𝗠𝗣𝗢𝗥𝗧𝗔𝗡𝗧 || 𝗥𝗘𝗔𝗗 𝗕𝗘𝗙𝗢𝗥𝗘 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚</blockquote>

<blockquote>⏳ Tʜɪs Vɪᴅᴇᴏ/Fɪʟᴇ Wɪʟʟ Bᴇ Dᴇʟᴇᴛᴇᴅ Iɴ <a href="https://t.me/{username}">{time}</a></blockquote>
<blockquote>(Dᴜᴇ Tᴏ Cᴏᴘʏʀɪɢʜᴛ Issᴜᴇs)</blockquote>

<blockquote>👉 Pʟᴇᴀsᴇ Fᴏʀᴡᴀʀᴅ Tʜɪs Fɪʟᴇ Tᴏ Sᴀᴠᴇᴅ Mᴇssᴀɢᴇs ᴏʀ Sᴏᴍᴇᴡʜᴇʀᴇ Eʟsᴇ Aɴᴅ Sᴛᴀʀᴛ Dᴏᴡɴʟᴏᴀᴅɪɴɢ Tʜᴇʀᴇ</blockquote>

‣ ᴜᴘᴅᴀᴛᴇs: <a href='https://t.me/paradoxbotz'>ᴘᴀʀᴀᴅᴏx ʙᴏᴛᴢ</a>
‣ ꜱᴜᴘᴘᴏʀᴛ: <a href='https://t.me/paradoxchats'>ᴘᴀʀᴀᴅᴏx ᴄʜᴀᴛꜱ</a></b></b>"""

#Function for provide auto delete notification message
async def auto_del_notification(bot_username, msg, delay_time, transfer): 
    temp = await msg.reply_text(DEL_MSG.format(username=bot_username, time=convert_time(delay_time)), disable_web_page_preview = True) 

    await asyncio.sleep(delay_time)
    try:
        if transfer:
            try:
                name = "♻️ Cʟɪᴄᴋ Hᴇʀᴇ"
                link = f"https://t.me/{bot_username}?start={transfer}"
                button = [[InlineKeyboardButton(text=name, url=link), InlineKeyboardButton(text="Cʟᴏsᴇ ✖️", callback_data = "close")]]

                await temp.edit_text(text=f"<b>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇs/Fɪʟᴇs ᴡᴇʀᴇ Sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ 🗑\n\n<blockquote>Iғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: [<a href={link}>{name}</a>] ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.</blockquote></b>", reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview = True)

            except Exception as e:
                await temp.edit_text(f"<b><blockquote>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ 🗑</blockquote></b>")
                print(f"Error occured while editing the Delete message: {e}")
        else:
            await temp.edit_text(f"<b><blockquote>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ 🗑</blockquote></b>")

    except Exception as e:
        print(f"Error occured while editing the Delete message: {e}")
        await temp.edit_text(f"<b><blockquote>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ 🗑</blockquote></b>")

    try: await msg.delete()
    except Exception as e: print(f"Error occurred on auto_del_notification() : {e}")


#Function for deleteing files/Messages.....
async def delete_message(msg, delay_time): 
    await asyncio.sleep(delay_time)
    
    try: await msg.delete()
    except Exception as e: print(f"Error occurred on delete_message() : {e}")
