import re
from bot import Bot
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove
from pyrogram.enums import ChatAction
from database.database import ocean
from config import OWNER_ID
from helper_func import S
from helper_func import is_admin

US_CMD_TEXT = """<b>~ Advanced Settings Panel</b>

<blockquote><b>Link Expiry:</b> <code>{expire_time}</code>
<b>Mask Button:</b> <code>{mask_status}</code></blockquote>

<i>Adjust your force-subscribe preferences below.</i>
"""


@Bot.on_message(filters.command('us') & filters.private & is_admin)
async def us_settings_command(client: Client, message: Message):
    await message.reply_chat_action(ChatAction.TYPING)
    await show_us_settings(message)


async def show_us_settings(message: Message | CallbackQuery):
    expire_seconds = await ocean.get_invite_expire_time()
    mask_name, mask_link = await ocean.get_mask_button()

    expire_display = f"{expire_seconds} seconds" if expire_seconds > 0 else "Disabled"
    mask_display = f"Active ({mask_name})" if mask_name and mask_link else "Disabled"

    buttons = [
        [
            InlineKeyboardButton(S('Set Expiry Time'), callback_data='us_set_expire'),
            InlineKeyboardButton(S('Set Mask Button'), callback_data='us_set_mask')
        ],
        [
            InlineKeyboardButton(S('Refresh'), callback_data='us_refresh'),
            InlineKeyboardButton(S('Close'), callback_data='close')
        ]
    ]

    text = S(US_CMD_TEXT.format(expire_time=expire_display, mask_status=mask_display))

    if isinstance(message, CallbackQuery):
        await message.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Bot.on_callback_query(filters.regex(r'^us_'), group=1)
async def us_callbacks(client: Bot, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    if data == 'us_refresh':
        await query.answer(S("Refreshing..."))
        await show_us_settings(query)

    elif data == 'us_set_expire':
        if not (user_id == OWNER_ID or await ocean.admin_exist(user_id)):
            return await query.answer(S("Access denied. Admins only."), show_alert=True)

        current_expire = await ocean.get_invite_expire_time()

        cancel_markup = ReplyKeyboardMarkup([['CANCEL']], one_time_keyboard=True, resize_keyboard=True)
        ask_msg = await client.ask(
            chat_id=user_id,
            text=S(
                f"<b><blockquote>Current Expiry: {current_expire} sec</blockquote>\n\n"
                f"Send the new expiry duration in seconds. You have 1 minute.\n"
                f"(Send <code>0</code> to disable link expiry)</b>"
            ),
            timeout=60,
            reply_markup=cancel_markup
        )

        if ask_msg.text == 'CANCEL':
            return await ask_msg.reply(S("<b><i>Cancelled.</i></b>"), reply_markup=ReplyKeyboardRemove())

        if ask_msg.text and ask_msg.text.isdigit():
            new_time = int(ask_msg.text)
            await ocean.set_invite_expire_time(new_time)
            await ask_msg.reply(
                S(f"<b>Done. Link expiry set to <code>{new_time}</code> seconds.</b>"),
                reply_markup=ReplyKeyboardRemove()
            )
            await show_us_settings(query)
        else:
            await ask_msg.reply(
                S("<b>Invalid input. Please send a numeric value.</b>"),
                reply_markup=ReplyKeyboardRemove()
            )

    elif data == 'us_set_mask':
        if not (user_id == OWNER_ID or await ocean.admin_exist(user_id)):
            return await query.answer(S("Access denied. Admins only."), show_alert=True)

        current_name, current_link = await ocean.get_mask_button()
        current_display = f"{current_name} - {current_link}" if current_name else "None"

        cancel_markup = ReplyKeyboardMarkup(
            [['CANCEL'], ['REMOVE MASK BUTTON']],
            one_time_keyboard=True,
            resize_keyboard=True
        )
        ask_msg = await client.ask(
            chat_id=user_id,
            text=S(
                f"<b><blockquote>Current Mask Button: {current_display}</blockquote>\n\n"
                f"Send the new mask button in this format: <code>Button Text - URL</code>\n\n"
                f"(Example: <code>Join VIP - https://example.com</code>)</b>"
            ),
            timeout=60,
            reply_markup=cancel_markup,
            disable_web_page_preview=True
        )

        if ask_msg.text == 'CANCEL':
            return await ask_msg.reply(S("<b><i>Cancelled.</i></b>"), reply_markup=ReplyKeyboardRemove())

        if ask_msg.text == 'REMOVE MASK BUTTON':
            await ocean.set_mask_button("", "")
            await ask_msg.reply(
                S("<b>Mask button removed.</b>"),
                reply_markup=ReplyKeyboardRemove()
            )
            return await show_us_settings(query)

        parts = ask_msg.text.split(' - ')
        if len(parts) == 2:
            btn_name = parts[0].strip()
            btn_link = parts[1].strip()
            await ocean.set_mask_button(btn_name, btn_link)
            await ask_msg.reply(
                S(f"<b>Mask button saved.\n<blockquote>{btn_name} -> {btn_link}</blockquote></b>"),
                reply_markup=ReplyKeyboardRemove()
            )
            await show_us_settings(query)
        else:
            await ask_msg.reply(
                S("<b>Wrong format. Use: <code>Button Text - URL</code></b>"),
                reply_markup=ReplyKeyboardRemove()
            )