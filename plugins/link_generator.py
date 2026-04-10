from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from helper_func import encode, get_message_id, is_admin
from helper_func import S


@Bot.on_message(filters.command('batch') & filters.private & is_admin)
async def batch(client: Client, message: Message):
    channel = f"<a href={client.db_channel_link}>{S('DB Channel')}</a>"

    # ── First message ─────────────────────────────────────────────
    while True:
        try:
            first_message = await client.ask(
                text=S(f"<b><blockquote>Forward the first message from {channel} (with quotes)..</blockquote>\n<blockquote>Or send the {channel} post link.</blockquote></b>"),
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception:
            return

        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply(
                S(f"<b>❌ Invalid.\n<blockquote>That post or link is not from my {channel}.</blockquote></b>"),
                quote=True
            )

    # ── Last message ──────────────────────────────────────────────
    while True:
        try:
            second_message = await client.ask(
                text=S(f"<b><blockquote>Now forward the last message from {channel} (with quotes)..</blockquote>\n<blockquote>Or send the {channel} post link.</blockquote></b>"),
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception:
            return

        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply(
                S(f"<b>❌ Invalid.\n<blockquote>That post or link is not from my {channel}.</blockquote></b>"),
                quote=True
            )

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(S("🔗 Share Link"), url=f'https://telegram.me/share/url?url={link}')
    ]])
    await second_message.reply_text(
        S(f"<b>Your batch link is ready:</b>\n<blockquote>{link}</blockquote>"),
        quote=True, reply_markup=reply_markup, disable_web_page_preview=True
    )


@Bot.on_message(filters.command('genlink') & filters.private & is_admin)
async def link_generator(client: Client, message: Message):
    channel = f"<a href={client.db_channel_link}>{S('DB Channel')}</a>"

    while True:
        try:
            channel_message = await client.ask(
                text=S(f"<b><blockquote>Forward the message from {channel} (with quotes)..</blockquote>\n<blockquote>Or send the {channel} post link.</blockquote></b>"),
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception:
            return

        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply(
                S(f"<b>❌ Invalid.\n<blockquote>That post or link is not from my {channel}.</blockquote></b>"),
                quote=True
            )

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(S("🔗 Share Link"), url=f'https://telegram.me/share/url?url={link}')
    ]])
    await channel_message.reply_text(
        S(f"<b>Your link is ready:</b>\n<blockquote>{link}</blockquote>"),
        quote=True, reply_markup=reply_markup, disable_web_page_preview=True
    )