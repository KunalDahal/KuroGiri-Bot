from bot import Bot
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove
from pyrogram.enums import ChatAction
from database.database import ocean
from config import OWNER_ID
from helper_func import is_admin

US_CMD_TEXT = """<b>⚙️ U-SETTINGS DASHBOARD ⚙️</b>

<blockquote><b>◈ Iɴᴠɪᴛᴇ Lɪɴᴋ Exᴘɪʀᴇ:</b> <code>{expire_time}</code>
<b>◈ Mᴀsᴋ Bᴜᴛᴛᴏɴ:</b> <code>{mask_status}</code></blockquote>

<i>Cᴏɴғɪɢᴜʀᴇ ʏᴏᴜʀ ᴀᴅᴠᴀɴᴄᴇᴅ ғᴏʀᴄᴇ sᴜʙ sᴇᴛᴛɪɴɢs ʙᴇʟᴏᴡ.</i>
"""

@Bot.on_message(filters.command('us') & filters.private & is_admin)
async def us_settings_command(client: Client, message: Message):
    await message.reply_chat_action(ChatAction.TYPING)
    await show_us_settings(message)

async def show_us_settings(message: Message | CallbackQuery):
    expire_seconds = await ocean.get_invite_expire_time()
    mask_name, mask_link = await ocean.get_mask_button()

    expire_display = f"{expire_seconds} sᴇᴄᴏɴᴅs" if expire_seconds > 0 else "Dɪsᴀʙʟᴇᴅ ❌"
    mask_display = f"Eɴᴀʙʟᴇᴅ ✅ ({mask_name})" if mask_name and mask_link else "Dɪsᴀʙʟᴇᴅ ❌"

    buttons = [
        [
            InlineKeyboardButton('⏱ Sᴇᴛ Exᴘɪʀᴇ Tɪᴍᴇ', callback_data='us_set_expire'),
            InlineKeyboardButton('🎭 Sᴇᴛ Mᴀsᴋ Bᴜᴛᴛᴏɴ', callback_data='us_set_mask')
        ],
        [
            InlineKeyboardButton('🔄 Rᴇғʀᴇsʜ', callback_data='us_refresh'),
            InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')
        ]
    ]

    text = US_CMD_TEXT.format(expire_time=expire_display, mask_status=mask_display)

    if isinstance(message, CallbackQuery):
        await message.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex(r'^us_'), group=1)
async def us_callbacks(client: Bot, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    
    if data == 'us_refresh':
        await query.answer("🔄 Rᴇғʀᴇsʜɪɴɢ...")
        await show_us_settings(query)

    elif data == 'us_set_expire':
        if not (user_id == OWNER_ID or await ocean.admin_exist(user_id)):
            return await query.answer("❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ Aᴅᴍɪɴ !", show_alert=True)
            
        current_expire = await ocean.get_invite_expire_time()
        
        cancel_markup = ReplyKeyboardMarkup([['CANCEL']], one_time_keyboard=True, resize_keyboard=True)
        ask_msg = await client.ask(
            chat_id=user_id,
            text=f"<b><blockquote>⏱ Cᴜʀʀᴇɴᴛ Exᴘɪʀᴇ Tɪᴍᴇ: {current_expire} sᴇᴄ</blockquote>\n\nSᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ᴇxᴘɪʀᴇ ᴛɪᴍᴇ ɪɴ sᴇᴄᴏɴᴅs ᴡɪᴛʜɪɴ 1 ᴍɪɴᴜᴛᴇ.\n(Sᴇɴᴅ <code>0</code> ᴛᴏ ᴅɪsᴀʙʟᴇ ᴇxᴘɪʀɪɴɢ ʟɪɴᴋs)</b>",
            timeout=60,
            reply_markup=cancel_markup
        )
        
        if ask_msg.text == 'CANCEL':
            return await ask_msg.reply("<b><i>🆑 Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>", reply_markup=ReplyKeyboardRemove())
            
        if ask_msg.text and ask_msg.text.isdigit():
            new_time = int(ask_msg.text)
            await ocean.set_invite_expire_time(new_time)
            await ask_msg.reply(f"<b>✅ Iɴᴠɪᴛᴇ Lɪɴᴋ Exᴘɪʀᴇ Tɪᴍᴇ sᴇᴛ ᴛᴏ <code>{new_time}</code> sᴇᴄᴏɴᴅs.</b>", reply_markup=ReplyKeyboardRemove())
            await show_us_settings(query)
        else:
            await ask_msg.reply("<b>❌ Iɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ. Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.</b>", reply_markup=ReplyKeyboardRemove())

    elif data == 'us_set_mask':
        if not (user_id == OWNER_ID or await ocean.admin_exist(user_id)):
            return await query.answer("❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ Aᴅᴍɪɴ !", show_alert=True)

        current_name, current_link = await ocean.get_mask_button()
        current_display = f"{current_name} - {current_link}" if current_name else "Nᴏɴᴇ"
        
        cancel_markup = ReplyKeyboardMarkup([['CANCEL'], ['REMOVE MASK BUTTON']], one_time_keyboard=True, resize_keyboard=True)
        ask_msg = await client.ask(
            chat_id=user_id,
            text=f"<b><blockquote>🎭 Cᴜʀʀᴇɴᴛ Mᴀsᴋ Bᴜᴛᴛᴏɴ: {current_display}</blockquote>\n\nSᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ᴍᴀsᴋ ʙᴜᴛᴛᴏɴ ɪɴ ғᴏʀᴍᴀᴛ: <code>Bᴜᴛᴛᴏɴ Tᴇxᴛ - URL</code>\n\n(Exᴀᴍᴘʟᴇ: <code>Jᴏɪɴ VIP - https://google.com</code>)</b>",
            timeout=60,
            reply_markup=cancel_markup,
            disable_web_page_preview=True
        )
        
        if ask_msg.text == 'CANCEL':
            return await ask_msg.reply("<b><i>🆑 Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>", reply_markup=ReplyKeyboardRemove())
            
        if ask_msg.text == 'REMOVE MASK BUTTON':
            await ocean.set_mask_button("", "")
            await ask_msg.reply("<b>✅ Mᴀsᴋ Bᴜᴛᴛᴏɴ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.</b>", reply_markup=ReplyKeyboardRemove())
            return await show_us_settings(query)
            
        parts = ask_msg.text.split(' - ')
        if len(parts) == 2:
            btn_name = parts[0].strip()
            btn_link = parts[1].strip()
            await ocean.set_mask_button(btn_name, btn_link)
            await ask_msg.reply(f"<b>✅ Mᴀsᴋ Bᴜᴛᴛᴏɴ sᴇᴛ sᴜᴄᴄᴇssғᴜʟʟʏ.\n<blockquote>{btn_name} ➪ {btn_link}</blockquote></b>", reply_markup=ReplyKeyboardRemove())
            await show_us_settings(query)
        else:
            await ask_msg.reply("<b>❌ Iɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ. Pʟᴇᴀsᴇ ᴜsᴇ <code>Bᴜᴛᴛᴏɴ Tᴇxᴛ - URL</code>.</b>", reply_markup=ReplyKeyboardRemove())
