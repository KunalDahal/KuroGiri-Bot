import os
import re
import asyncio
from asyncio import Lock
from bot import Bot
from config import OWNER_ID, SUPPORT_GROUP
from helper_func import S
import time
from datetime import datetime
from pyrogram import Client, filters
from helper_func import is_admin, get_readable_time, banUser
from plugins.FORMATS import HELP_TEXT, BAN_TXT, CMD_TXT, USER_CMD_TXT, FSUB_CMD_TXT
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from database.database import ocean
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


REPLY_ERROR = S("Reply to a Telegram message with this command — no extra arguments needed.")
is_canceled = False
cancel_lock = Lock()


@Bot.on_message(banUser & filters.private & filters.command(['start']))
async def handle_banuser(client, message):
    return await message.reply(text=BAN_TXT, message_effect_id=5046589136895476101)

@Bot.on_message(filters.command('cancel') & filters.private & is_admin)
async def cancel_broadcast(client: Bot, message: Message):
    global is_canceled
    async with cancel_lock:
        is_canceled = True

@Bot.on_message(filters.command('broadcast') & filters.private & is_admin)
async def send_text(client: Bot, message: Message):
    global is_canceled
    async with cancel_lock:
        is_canceled = False
    mode = False
    broad_mode = ''
    store = message.text.split()[1:]

    if store and len(store) == 1 and store[0] == 'silent':
        mode = True
        broad_mode = 'SILENT '

    if message.reply_to_message:
        query = await ocean.full_userbase()
        broadcast_msg = message.reply_to_message
        total = len(query)
        successful = blocked = deleted = unsuccessful = 0

        pls_wait = await message.reply(S("<i>Sending broadcast... This may take a while.</i>"))
        bar_length = 20
        final_progress_bar = "●" * bar_length
        complete_msg = S(f"📡 {broad_mode}BROADCAST COMPLETE ✅")
        progress_bar = ''
        last_update_percentage = 0
        percent_complete = 0
        update_interval = 0.05

        for i, chat_id in enumerate(query, start=1):
            async with cancel_lock:
                if is_canceled:
                    final_progress_bar = progress_bar
                    complete_msg = S(f"📡 {broad_mode}BROADCAST STOPPED ❌")
                    break
            try:
                await broadcast_msg.copy(chat_id, disable_notification=mode)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id, disable_notification=mode)
                successful += 1
            except UserIsBlocked:
                await ocean.del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await ocean.del_user(chat_id)
                deleted += 1
            except Exception:
                unsuccessful += 1
                await ocean.del_user(chat_id)

            percent_complete = i / total

            if percent_complete - last_update_percentage >= update_interval or last_update_percentage == 0:
                num_blocks = int(percent_complete * bar_length)
                progress_bar = "●" * num_blocks + "○" * (bar_length - num_blocks)

                status_update = S(f"""<b>📡 {broad_mode}BROADCAST RUNNING...

<blockquote>⏳:</b> [{progress_bar}] <code>{percent_complete:.0%}</code></blockquote>

<b>👥 Total Users: <code>{total}</code>
✅ Delivered: <code>{successful}</code>
🚫 Blocked: <code>{blocked}</code>
⚠️ Deactivated: <code>{deleted}</code>
❌ Failed: <code>{unsuccessful}</code></b>

<i>➜ Use /cancel to halt the broadcast.</i>""")
                await pls_wait.edit(status_update)
                last_update_percentage = percent_complete

        final_status = S(f"""<b>{complete_msg}

<blockquote>Done:</b> [{final_progress_bar}] {percent_complete:.0%}</blockquote>

<b>👥 Total Users: <code>{total}</code>
✅ Delivered: <code>{successful}</code>
🚫 Blocked: <code>{blocked}</code>
⚠️ Deactivated: <code>{deleted}</code>
❌ Failed: <code>{unsuccessful}</code></b>""")
        return await pls_wait.edit(final_status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()


@Bot.on_message(filters.command('status') & filters.private & is_admin)
async def info(client: Bot, message: Message):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])

    start_time = time.time()
    temp_msg = await message.reply(S("<b><i>Fetching data...</i></b>"), quote=True)
    end_time = time.time()

    ping_time = (end_time - start_time) * 1000
    users = await ocean.full_userbase()
    now = datetime.now()
    delta = now - client.uptime
    bottime = get_readable_time(delta.seconds)

    await temp_msg.edit(
        S(f"👥 : <b>{len(users)} USERS\n\n🤖 UPTIME » {bottime}\n\n📶 PING » {ping_time:.2f} ms</b>"),
        reply_markup=reply_markup,
    )


@Bot.on_message(filters.command('cmd') & filters.private & is_admin)
async def bcmd(bot: Bot, message: Message):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])
    await message.reply(text=CMD_TXT, reply_markup=reply_markup, quote=True)

@Bot.on_message(filters.command('forcesub') & filters.private & ~banUser)
async def fsub_commands(client: Client, message: Message):
    button = [[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]]
    await message.reply(text=FSUB_CMD_TXT, reply_markup=InlineKeyboardMarkup(button), quote=True)


@Bot.on_message(filters.command('users') & filters.private & ~banUser)
async def user_setting_commands(client: Client, message: Message):
    button = [[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]]
    await message.reply(text=USER_CMD_TXT, reply_markup=InlineKeyboardMarkup(button), quote=True)