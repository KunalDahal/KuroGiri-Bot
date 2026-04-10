import re
import random
from bot import Bot
from config import OWNER_ID, PICS
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
)
from helper_func import banUser, is_admin
from database.database import ocean
from plugins.FORMATS import HELP_TEXT
from helper_func import S

# ══════════════════════════════════════════════════════════════════════════════
#                          ADMIN / OWNER HELP TEXTS
# ══════════════════════════════════════════════════════════════════════════════

HELP_PANEL_MAIN = S("""<b>📖 Hey {first}, welcome to the Help Panel!

<blockquote expandable>➪ I am an advanced file-sharing bot with powerful admin tools, built to distribute content securely via encoded links.

➪ Use the buttons below to browse each help section.</blockquote>

‣ Updates: <a href='https://t.me/OceanXBotz'>OceanXBotz</a>
‣ Support: <a href='https://t.me/Anime_Ocean_Official'>Animes Ocean</a></b>""")


HELP_ADMIN_CMDS = S("""<b>🤖 ADMIN COMMANDS

<blockquote expandable>
📢 /broadcast
↳ Push a message out to every bot user.
   Usage: Reply to any message with /broadcast
   Option: /broadcast silent — no notification sound

🛑 /cancel
↳ Stop a broadcast that is currently running.

📊 /status
↳ Check total users, uptime and ping.

📋 /cmd
↳ View a quick summary of admin commands.

🔗 /batch
↳ Generate a single link that delivers a range of messages (e.g. episode batches) at once.

🔗 /genlink
↳ Generate a shareable link for one specific message from your DB Channel.

🔗 /flink
↳ Generate multiple quality links in a custom format (e.g. 360P, 720P, 1080P).

📡 /fsub_chnl
↳ List all currently active force-sub channels.

🚫 /banuser_list
↳ View everyone who is currently banned.

🚫 /add_banuser [user_id(s)]
↳ Ban one or more users.

✅ /del_banuser [user_id(s) | all]
↳ Unban user(s) or clear every ban at once.
</blockquote></b>""")


HELP_OWNER_CMDS = S("""<b>👑 OWNER-ONLY COMMANDS

<blockquote expandable>
➕ /add_fsub [channel_id(s)]
↳ Register one or more channel IDs as force-sub.
   Example: /add_fsub -100xxxxxxxxxx

➖ /del_fsub [channel_id(s) | all]
↳ Remove specific channels or wipe all force-sub entries.
   Example: /del_fsub all

👤 /admin_list
↳ View all current bot admins.

➕ /add_admins [user_id(s)]
↳ Grant admin access to one or more users.
   Example: /add_admins 123456789 987654321

➖ /del_admins [user_id(s) | all]
↳ Revoke admin access from user(s).
   Example: /del_admins all

🔄 /restart
↳ Restart the bot instance.
</blockquote></b>""")


HELP_SETTINGS = S("""<b>⚙️ SETTINGS & CONFIGURATION

<blockquote expandable>
🗑 /auto_del
↳ Control auto-delete mode and its timer.
   When active, all delivered files are removed after the set duration.

📁 /files
↳ Manage all file-related settings:
   • 🔒 Protect Content — prevent users from forwarding or saving files
   • 🫥 Hide Caption — strip captions from documents and audios before delivery
   • 🔘 Channel Button — attach a custom inline button to every delivered file

📢 /req_fsub
↳ Toggle Request Force-Sub mode ON or OFF.
   When ON, private channels use join-request flow instead of direct membership check.
   Also gives access to advanced request-link management.

🛠 /us (User-Settings)
↳ Advanced configurations:
   • ⏱ Set Invite Link Expiry — auto-rotate invite links at set intervals
   • 🎭 Set Mask Button — add a custom button on the force-sub screen
</blockquote></b>""")


HELP_FEATURES = S("""<b>✨ FEATURES OVERVIEW

<blockquote expandable>
🔐 Force Sub — Users must join all channels before accessing files. Supports public & private channels.

🚦 Request FSub — Private channel join-request flow; user is granted access once request is sent.

🗑 Auto Delete — Files auto-removed after a set timer with a re-download button sent to the user.

🔒 Protect Content — Prevents forwarding or saving of delivered files.

🫥 Hide Caption — Strips captions from documents & audios before delivery.

🔘 Channel Button — Adds a custom inline button to every delivered file.

🎭 Mask Button — Custom button on the force-sub screen linking to any URL.

⏱ Link Expiry — Time-limited invite links, auto-rotated and cached.

📢 Broadcast — Send any message to all users with live progress bar. Silent mode supported.

🔗 /flink — Multi-quality links (360P / 720P / 1080P / 4K) with inline buttons.

🚫 Ban System — Block users from interacting with the bot.

👥 Admin System — Grant trusted users admin-level access.
</blockquote></b>""")


HELP_FSUB_CMDS = S("""<b>📡 FORCE-SUB COMMANDS

<blockquote expandable>
📋 /forcesub
↳ View all force-sub related commands.

📋 /fsub_chnl (admins)
↳ List all active force-sub channels with their names and IDs.

➕ /add_fsub [channel_id(s)] (owner)
↳ Add one or more channel IDs. The bot must be admin in each channel.
   Example: /add_fsub -100xxxxxxxxxx -100yyyyyyyyyy

➖ /del_fsub [channel_id(s) | all] (owner)
↳ Remove specific channels or clear all at once.
   Example: /del_fsub all

📢 /req_fsub
↳ Toggle Request Force-Sub mode ON or OFF. Also access:
   • List of request channels and their user counts
   • Clear user data per channel
   • Delete channel data entirely
   • Revoke and clear stored request links
</blockquote></b>""")


HELP_USER_CMDS = S("""<b>👤 USER MANAGEMENT COMMANDS

<blockquote expandable>
📋 /admin_list (owner)
↳ View all current bot admins.

➕ /add_admins [user_id(s)] (owner)
↳ Add one or more users as bot admins. Admins can use all admin-level commands.

➖ /del_admins [user_id(s) | all] (owner)
↳ Revoke admin privileges from user(s).

📋 /banuser_list (admins)
↳ View all banned users with their names.

🚫 /add_banuser [user_id(s)] (admins)
↳ Ban one or more users. Banned users cannot use /start or /help.

✅ /del_banuser [user_id(s) | all] (admins)
↳ Unban user(s) or clear the entire ban list.

📋 /users
↳ View all user management commands.
</blockquote></b>""")


# ══════════════════════════════════════════════════════════════════════════════
#                          KEYBOARD BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def main_help_keyboard(user_id: int, is_owner: bool, is_adm: bool):
    buttons = [
        [
            InlineKeyboardButton(S("🤖 Admin Cmds"),   callback_data="help:admin"),
            InlineKeyboardButton(S("✨ Features"),      callback_data="help:features"),
        ],
        [
            InlineKeyboardButton(S("📡 Force Sub"),     callback_data="help:fsub"),
            InlineKeyboardButton(S("👤 User Mgmt"),     callback_data="help:users"),
        ],
        [
            InlineKeyboardButton(S("⚙️ Settings"),      callback_data="help:settings"),
        ],
    ]
    if is_owner:
        buttons.append([InlineKeyboardButton(S("👑 Owner Cmds"), callback_data="help:owner")])
    buttons.append([InlineKeyboardButton(S("Close ✖️"), callback_data="close")])
    return InlineKeyboardMarkup(buttons)


def back_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(S("⬅️ Back"),   callback_data="help:main"),
        InlineKeyboardButton(S("Close ✖️"), callback_data="close")
    ]])


# ══════════════════════════════════════════════════════════════════════════════
#                             /help COMMAND
# Admins / Owner  →  full interactive help panel with sections
# Regular users   →  HELP_TEXT from FORMATS.py (simple user guide)
# ══════════════════════════════════════════════════════════════════════════════

@Bot.on_message(filters.command('help') & filters.private & ~banUser)
async def help_command(client: Client, message: Message):
    await message.reply_chat_action(ChatAction.UPLOAD_PHOTO)

    user_id  = message.from_user.id
    is_owner = (user_id == OWNER_ID)
    is_adm   = is_owner or await ocean.admin_exist(user_id)

    if is_adm:
        # ── Admin / Owner: full help panel ────────────────────────
        await message.reply_photo(
            photo    = random.choice(PICS),
            caption  = HELP_PANEL_MAIN.format(
                first   = message.from_user.first_name,
                mention = message.from_user.mention,
            ),
            reply_markup      = main_help_keyboard(user_id, is_owner, is_adm),
            message_effect_id = 5046509860389126442,
        )
    else:
        from config import SUPPORT_GROUP
        buttons = []
        if SUPPORT_GROUP:
            buttons.append([InlineKeyboardButton(S("🌐 Support Group"), url=SUPPORT_GROUP)])
        buttons.append([InlineKeyboardButton(S("Close ✖️"), callback_data="close")])

        await message.reply_photo(
            photo    = random.choice(PICS),
            caption  = HELP_TEXT.format(
                mention = message.from_user.mention,
            ),
            reply_markup      = InlineKeyboardMarkup(buttons),
            message_effect_id = 5046509860389126442,
        )

    try:
        await message.delete()
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#                        CALLBACK QUERY HANDLER
# ══════════════════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "help:admin":    (HELP_ADMIN_CMDS,  "https://i.ibb.co/hxTXzhrm/help.png"),
    "help:owner":    (HELP_OWNER_CMDS,  "https://i.ibb.co/hxTXzhrm/help.png"),
    "help:settings": (HELP_SETTINGS,    "https://i.ibb.co/hxTXzhrm/help.png"),
    "help:features": (HELP_FEATURES,    "https://i.ibb.co/hxTXzhrm/help.png"),
    "help:fsub":     (HELP_FSUB_CMDS,   "https://i.ibb.co/hxTXzhrm/help.png"),
    "help:users":    (HELP_USER_CMDS,   "https://i.ibb.co/hxTXzhrm/help.png"),
}


@Bot.on_callback_query(filters.regex(r'^help:'))
async def help_callback(client: Bot, query: CallbackQuery):
    data    = query.data
    user_id = query.from_user.id

    # owner-only guard
    if data == "help:owner" and user_id != OWNER_ID:
        return await query.answer(S("❌ This section is for the owner only."), show_alert=True)

    # back to main panel
    if data == "help:main":
        is_owner = (user_id == OWNER_ID)
        is_adm   = is_owner or await ocean.admin_exist(user_id)
        await query.edit_message_media(
            InputMediaPhoto(
                media   = random.choice(PICS),
                caption = HELP_PANEL_MAIN.format(
                    first   = query.from_user.first_name,
                    mention = query.from_user.mention,
                )
            ),
            reply_markup = main_help_keyboard(user_id, is_owner, is_adm)
        )
        return await query.answer()

    # section pages
    if data in SECTION_MAP:
        caption, photo = SECTION_MAP[data]
        try:
            await query.edit_message_media(
                InputMediaPhoto(media=photo, caption=caption),
                reply_markup = back_keyboard()
            )
        except Exception:
            await query.edit_message_caption(
                caption      = caption,
                reply_markup = back_keyboard()
            )
        return await query.answer()

    await query.answer()