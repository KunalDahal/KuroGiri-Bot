import os
import re
import sys
import time
import random
import asyncio
import subprocess
from bot import Bot
from database.database import ocean
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from plugins.FORMATS import START_MSG, FORCE_MSG
from pyrogram.enums import ParseMode, ChatAction
from datetime import datetime
from config import CUSTOM_CAPTION, OWNER_ID, PICS
from plugins.autoDelete import auto_del_notification, delete_message
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import banUser, is_userJoin, is_admin, subscribed, encode, decode, get_messages
from helper_func import S

@Bot.on_message(filters.command('start') & filters.private & ~banUser & subscribed)
async def start_command(client: Client, message: Message):
    await message.reply_chat_action(ChatAction.CHOOSE_STICKER)
    id = message.from_user.id

    if not await ocean.present_user(id):
        try: await ocean.add_user(id)
        except: pass

    text = message.text
    if len(text) > 7:
        await message.delete()

        try: base64_string = text.split(" ", 1)[1]
        except: return

        string = await decode(base64_string)
        argument = string.split("-")

        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return

            if start <= end:
                ids = range(start, end + 1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break

        elif len(argument) == 2:
            try: ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except: return

        last_message = None
        await message.reply_chat_action(ChatAction.UPLOAD_DOCUMENT)

        try: messages = await get_messages(client, ids)
        except: return await message.reply(S("<b><i>Could not fetch the content. Try again later.</i></b>"))

        AUTO_DEL, DEL_TIMER, HIDE_CAPTION, CHNL_BTN, PROTECT_MODE = await asyncio.gather(
            ocean.get_auto_delete(), ocean.get_del_timer(), ocean.get_hide_caption(),
            ocean.get_channel_button(), ocean.get_protect_content()
        )
        if CHNL_BTN:
            button_name, button_link = await ocean.get_channel_button_link()

        for idx, msg in enumerate(messages):
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                )
            elif HIDE_CAPTION and (msg.document or msg.audio):
                caption = ""
            else:
                caption = "" if not msg.caption else msg.caption.html

            if CHNL_BTN:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=button_name, url=button_link)]]) \
                    if msg.document or msg.photo or msg.video or msg.audio else None
            else:
                reply_markup = msg.reply_markup

            try:
                copied_msg = await msg.copy(
                    chat_id=id, caption=caption,
                    parse_mode=ParseMode.HTML, reply_markup=reply_markup,
                    protect_content=PROTECT_MODE
                )
                await asyncio.sleep(0.1)

                if AUTO_DEL:
                    asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                    if idx == len(messages) - 1:
                        last_message = copied_msg

            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(
                    chat_id=id, caption=caption,
                    parse_mode=ParseMode.HTML, reply_markup=reply_markup,
                    protect_content=PROTECT_MODE
                )
                await asyncio.sleep(0.1)

                if AUTO_DEL:
                    asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                    if idx == len(messages) - 1:
                        last_message = copied_msg

        if AUTO_DEL and last_message:
            asyncio.create_task(auto_del_notification(client.username, last_message, DEL_TIMER, message.command[1]))

    else:
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(S('About Me'), callback_data='about'),
                InlineKeyboardButton(S('Settings'), callback_data='setting')
            ]
        ])

        await message.reply_photo(
            photo=random.choice(PICS),
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            message_effect_id=5104841245755180586
        )
        try: await message.delete()
        except: pass


##===================================================================================================================##
# TRIGGERED START MESSAGE — HANDLES FORCE SUB PROMPT WHEN USER HAS NOT JOINED REQUIRED CHANNELS
##===================================================================================================================##

chat_data_cache = {}

@Bot.on_message(filters.command('start') & filters.private & ~banUser)
async def not_joined(client: Client, message: Message):
    temp = await message.reply(S("<b>Verifying access...</b>"))

    user_id = message.from_user.id

    REQFSUB = await ocean.get_request_forcesub()
    INVITE_EXPIRE_TIME = await ocean.get_invite_expire_time()
    MASK_BUTTON_NAME, MASK_BUTTON_LINK = await ocean.get_mask_button()

    channel_buttons = []
    count = 0

    try:
        for total, chat_id in enumerate(await ocean.get_all_channels(), start=1):
            await message.reply_chat_action(ChatAction.PLAYING)

            if not await is_userJoin(client, user_id, chat_id):
                try:
                    if chat_id in chat_data_cache:
                        data = chat_data_cache[chat_id]
                    else:
                        data = await client.get_chat(chat_id)
                        chat_data_cache[chat_id] = data

                    cname = data.title
                    link = None
                    link_data = await ocean.get_stored_reqLink(chat_id)

                    if link_data:
                        link = link_data.get('link')
                        expire_at = link_data.get('expire_at')

                        if (expire_at and time.time() > expire_at) or (not expire_at and INVITE_EXPIRE_TIME > 0):
                            try:
                                if link:
                                    await client.revoke_chat_invite_link(chat_id, link)
                            except: pass
                            link = None

                    if REQFSUB and not bool(data.username):
                        await ocean.add_reqChannel(chat_id)

                        if not link:
                            expire_date_int = int(time.time() + INVITE_EXPIRE_TIME) if INVITE_EXPIRE_TIME > 0 else None
                            expire_date = datetime.fromtimestamp(expire_date_int + 5) if expire_date_int else None

                            invite = await client.create_chat_invite_link(
                                chat_id=chat_id, creates_join_request=True, expire_date=expire_date
                            )
                            link = invite.invite_link
                            await ocean.store_reqLink(chat_id, link, expire_at=expire_date_int)
                    else:
                        if INVITE_EXPIRE_TIME > 0:
                            if not link:
                                expire_date_int = int(time.time() + INVITE_EXPIRE_TIME)
                                expire_date = datetime.fromtimestamp(expire_date_int + 5)

                                invite = await client.create_chat_invite_link(chat_id=chat_id, expire_date=expire_date)
                                link = invite.invite_link
                                await ocean.store_reqLink(chat_id, link, expire_at=expire_date_int)
                        else:
                            if not link:
                                link = data.invite_link
                                if not link:
                                    invite = await client.create_chat_invite_link(chat_id=chat_id)
                                    link = invite.invite_link
                                await ocean.store_reqLink(chat_id, link)

                    channel_buttons.append(InlineKeyboardButton(
                        text=S(f"Join Channel {count + 1}"), url=link
                    ))
                    count += 1
                    await temp.edit(S(f"<b>Checking {count} channel(s)...</b>"))

                except Exception as e:
                    print(f"Can't Export Channel Name and Link..., Please Check If the Bot is admin in the FORCE SUB CHANNELS:\nProvided Force sub Channel:- {chat_id}")
                    return await temp.edit(S(
                        f"<b><i>Setup error detected. Reach out to the developer — @OceanXBotz</i></b>\n"
                        f"<blockquote expandable><b>Reason:</b> {e}</blockquote>"
                    ))

        buttons = [channel_buttons[i:i + 2] for i in range(0, len(channel_buttons), 2)]

        if MASK_BUTTON_NAME and MASK_BUTTON_LINK:
            mask_button = InlineKeyboardButton(text=S(MASK_BUTTON_NAME), url=MASK_BUTTON_LINK)
            if count % 2 != 0:
                buttons[-1].append(mask_button)
            else:
                buttons.append([mask_button])

        try:
            buttons.append([InlineKeyboardButton(
                text=S("Try Again"),
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )])
        except IndexError:
            pass

        await message.reply_chat_action(ChatAction.CANCEL)
        await temp.edit(
            text=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id,
                count=count,
                total=total
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )

        try: await message.delete()
        except: pass

    except Exception as e:
        print(f"Unable to perform forcesub buttons reason : {e}")
        return await temp.edit(S(
            f"<b><i>An unexpected error occurred. Contact the developer — @OceanXBotz</i></b>\n"
            f"<blockquote expandable><b>Reason:</b> {e}</blockquote>"
        ))


##===================================================================================================================##
# RESTART COMMAND
##===================================================================================================================##

@Bot.on_message(filters.command('restart') & filters.private & filters.user(OWNER_ID))
async def restart_bot(client: Client, message: Message):
    print("Restarting bot...")
    msg = await message.reply(text=S(f"<b><i><blockquote>~ {client.name} is restarting, hold on...</blockquote></i></b>"))
    try:
        await asyncio.sleep(6)
        await msg.delete()
        args = [sys.executable, "main.py"]
        os.execl(sys.executable, *args)
    except Exception as e:
        print(f"Error occured while Restarting the bot: {e}")
        return await msg.edit_text(S(
            f"<b><i>Restart failed. Contact the developer — @OceanXBotz</i></b>\n"
            f"<blockquote expandable><b>Reason:</b> {e}</blockquote>"
        ))