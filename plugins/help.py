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

# ══════════════════════════════════════════════════════════════════
#                        HELP PANEL TEXTS
# ══════════════════════════════════════════════════════════════════

HELP_PANEL_MAIN = """<b>📖 Hᴇʟʟᴏ {first}, Wᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ Hᴇʟᴘ Pᴀɴᴇʟ !

<blockquote expandable>➪ I ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇ ғɪʟᴇ-sʜᴀʀɪɴɢ ʙᴏᴛ ᴡɪᴛʜ ᴘᴏᴡᴇʀғᴜʟ ᴀᴅᴍɪɴ ᴛᴏᴏʟs, ʙᴜɪʟᴛ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴅɪsᴛʀɪʙᴜᴛᴇ ᴄᴏɴᴛᴇɴᴛ sᴇᴄᴜʀᴇʟʏ ᴠɪᴀ ᴇɴᴄᴏᴅᴇᴅ ʟɪɴᴋs.

➪ Usᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ɴᴀᴠɪɢᴀᴛᴇ ᴛʜᴇ ʜᴇʟᴘ sᴇᴄᴛɪᴏɴs.</blockquote>

‣ ᴜᴘᴅᴀᴛᴇs: <a href='https://t.me/OceanXBotz'>ᴏᴄᴇᴀɴxʙᴏᴛᴢ</a>
‣ ꜱᴜᴘᴘᴏʀᴛ: <a href='https://t.me/Anime_Ocean_Official'>ᴀɴɪᴍᴇs ᴏᴄᴇᴀɴ</a></b>"""


HELP_ADMIN_CMDS = """<b>🤖 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦

<blockquote expandable>
📢 <b>/broadcast</b>
↳ Bʀᴏᴀᴅᴄᴀsᴛ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ʙᴏᴛ ᴜsᴇʀs.
   ᴜsᴀɢᴇ: Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ /broadcast
   ᴏᴘᴛɪᴏɴ: <code>/broadcast silent</code> — ɴᴏ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ

🛑 <b>/cancel</b>
↳ Cᴀɴᴄᴇʟ ᴀɴ ᴏɴɢᴏɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ.

📊 <b>/status</b>
↳ Vɪᴇᴡ ᴛᴏᴛᴀʟ ᴜsᴇʀs, ʙᴏᴛ ᴜᴘᴛɪᴍᴇ ᴀɴᴅ ᴘɪɴɢ.

📋 <b>/cmd</b>
↳ Vɪᴇᴡ ᴀ sʜᴏʀᴛ sᴜᴍᴍᴀʀʏ ᴏғ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs.

🔗 <b>/batch</b>
↳ Gᴇɴᴇʀᴀᴛᴇ ᴏɴᴇ ʟɪɴᴋ ᴛʜᴀᴛ sᴇɴᴅs ᴀ ʀᴀɴɢᴇ ᴏғ
   ᴍᴇssᴀɢᴇs (ᴇᴘɪsᴏᴅᴇ ʙᴀᴛᴄʜᴇs ᴇᴛᴄ.) ᴀᴛ ᴏɴᴄᴇ.

🔗 <b>/genlink</b>
↳ Gᴇɴᴇʀᴀᴛᴇ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ғᴏʀ ᴀ sɪɴɢʟᴇ
   ᴍᴇssᴀɢᴇ ғʀᴏᴍ ʏᴏᴜʀ Dʙ Cʜᴀɴɴᴇʟ.

🔗 <b>/flink</b>
↳ Gᴇɴᴇʀᴀᴛᴇ ᴍᴜʟᴛɪᴘʟᴇ ǫᴜᴀʟɪᴛʏ ʟɪɴᴋs ɪɴ ᴀ
   ᴄᴜsᴛᴏᴍ ғᴏʀᴍᴀᴛ (ᴇ.ɢ. 360P, 720P, 1080P).

📡 <b>/fsub_chnl</b>
↳ Vɪᴇᴡ ᴀʟʟ ᴄᴜʀʀᴇɴᴛ ғᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟs.

🚫 <b>/banuser_list</b>
↳ Vɪᴇᴡ ᴀʟʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀs.

🚫 <b>/add_banuser</b> [user_id(s)]
↳ Bᴀɴ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀs.

✅ <b>/del_banuser</b> [user_id(s) | all]
↳ Uɴʙᴀɴ ᴜsᴇʀ(s) ᴏʀ ᴄʟᴇᴀʀ ᴀʟʟ ʙᴀɴs.
</blockquote></b>"""


HELP_OWNER_CMDS = """<b>👑 𝗢𝗪𝗡𝗘𝗥-𝗢𝗡𝗟𝗬 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦

<blockquote expandable>
➕ <b>/add_fsub</b> [channel_id(s)]
↳ Aᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴄʜᴀɴɴᴇʟ ɪᴅs ᴀs ғᴏʀᴄᴇ-sᴜʙ.
   ᴇxᴀᴍᴘʟᴇ: <code>/add_fsub -100xxxxxxxxxx</code>

➖ <b>/del_fsub</b> [channel_id(s) | all]
↳ Rᴇᴍᴏᴠᴇ ᴏɴᴇ, ᴍᴜʟᴛɪᴘʟᴇ, ᴏʀ ᴀʟʟ ғᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟs.
   ᴇxᴀᴍᴘʟᴇ: <code>/del_fsub all</code>

👤 <b>/admin_list</b>
↳ Vɪᴇᴡ ᴀʟʟ ᴄᴜʀʀᴇɴᴛ ʙᴏᴛ ᴀᴅᴍɪɴs.

➕ <b>/add_admins</b> [user_id(s)]
↳ Gʀᴀɴᴛ ᴀᴅᴍɪɴ ᴀᴄᴄᴇss ᴛᴏ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀs.
   ᴇxᴀᴍᴘʟᴇ: <code>/add_admins 123456789 987654321</code>

➖ <b>/del_admins</b> [user_id(s) | all]
↳ Rᴇᴠᴏᴋᴇ ᴀᴅᴍɪɴ ᴀᴄᴄᴇss ғʀᴏᴍ ᴜsᴇʀ(s).
   ᴇxᴀᴍᴘʟᴇ: <code>/del_admins all</code>

🔄 <b>/restart</b>
↳ Rᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ɪɴsᴛᴀɴᴄᴇ (ᴏᴡɴᴇʀ ᴏɴʟʏ).
</blockquote></b>"""


HELP_SETTINGS = """<b>⚙️ 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 & 𝗖𝗢𝗡𝗙𝗜𝗚𝗨𝗥𝗔𝗧𝗜𝗢𝗡𝗦

<blockquote expandable>
🗑 <b>/auto_del</b>
↳ Cᴏɴᴛʀᴏʟ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ ᴀɴᴅ ᴛɪᴍᴇʀ.
   ᴡʜᴇɴ ᴇɴᴀʙʟᴇᴅ, ᴀʟʟ sᴇɴᴛ ғɪʟᴇs ᴀʀᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ
   ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ ᴛʜᴇ sᴇᴛ ᴛɪᴍᴇʀ ᴇxᴘɪʀᴇs.

📁 <b>/files</b>
↳ Mᴀɴᴀɢᴇ ᴀʟʟ ғɪʟᴇ-ʀᴇʟᴀᴛᴇᴅ sᴇᴛᴛɪɴɢs:
   • 🔒 Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ — ᴘʀᴇᴠᴇɴᴛ ᴜsᴇʀs ғʀᴏᴍ
     ғᴏʀᴡᴀʀᴅɪɴɢ / sᴀᴠɪɴɢ ғɪʟᴇs
   • 🫥 Hɪᴅᴇ Cᴀᴘᴛɪᴏɴ — sᴛʀɪᴘ ᴄᴀᴘᴛɪᴏɴ ғʀᴏᴍ
     ᴅᴏᴄᴜᴍᴇɴᴛs / ᴀᴜᴅɪᴏs ᴡʜᴇɴ sᴇɴᴛ
   • 🔘 Cʜᴀɴɴᴇʟ Bᴜᴛᴛᴏɴ — ᴀᴛᴛᴀᴄʜ ᴀ ᴄᴜsᴛᴏᴍ
     ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴇᴠᴇʀʏ ᴅᴇʟɪᴠᴇʀᴇᴅ ғɪʟᴇ

📢 <b>/req_fsub</b>
↳ Eɴᴀʙʟᴇ / Dɪsᴀʙʟᴇ Rᴇǫᴜᴇsᴛ Fᴏʀᴄᴇ Sᴜʙ ᴍᴏᴅᴇ.
   ᴡʜᴇɴ ᴏɴ, ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟs ᴜsᴇ ᴊᴏɪɴ-ʀᴇǫᴜᴇsᴛ
   ɪɴsᴛᴇᴀᴅ ᴏғ ᴅɪʀᴇᴄᴛ ᴍᴇᴍʙᴇʀsʜɪᴘ ᴄʜᴇᴄᴋ.
   ᴀʟsᴏ ᴀᴄᴄᴇss ᴀᴅᴠᴀɴᴄᴇᴅ ʀᴇǫᴜᴇsᴛ-ʟɪɴᴋ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ.

🛠 <b>/us</b> (U-Sᴇᴛᴛɪɴɢs)
↳ Aᴅᴠᴀɴᴄᴇᴅ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴs:
   • ⏱ Sᴇᴛ Iɴᴠɪᴛᴇ Lɪɴᴋ Exᴘɪʀᴇ Tɪᴍᴇ — ʀᴏᴛᴀᴛᴇ
     ɪɴᴠɪᴛᴇ ʟɪɴᴋs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴛ sᴇᴛ ɪɴᴛᴇʀᴠᴀʟs
   • 🎭 Sᴇᴛ Mᴀsᴋ Bᴜᴛᴛᴏɴ — ᴀᴅᴅ ᴀ ᴄᴜsᴛᴏᴍ ʙᴜᴛᴛᴏɴ
     ɪɴ ᴛʜᴇ ғᴏʀᴄᴇ-sᴜʙ sᴄʀᴇᴇɴ (ᴇ.ɢ. Jᴏɪɴ VIP)
</blockquote></b>"""


HELP_FEATURES = """<b>✨ 𝗙𝗘𝗔𝗧𝗨𝗥𝗘𝗦 𝗢𝗩𝗘𝗥𝗩𝗜𝗘𝗪

<blockquote expandable>
🔐 𝗙𝗼𝗿𝗰𝗲 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻
↳ Usᴇʀs ᴍᴜsᴛ ᴊᴏɪɴ ᴀʟʟ ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs
   ʙᴇғᴏʀᴇ ᴀᴄᴄᴇssɪɴɢ ᴀɴʏ ғɪʟᴇs. Sᴜᴘᴘᴏʀᴛs ʙᴏᴛʜ
   ᴘᴜʙʟɪᴄ ᴀɴᴅ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟs.

🚦 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝗙𝗼𝗿𝗰𝗲 𝗦𝘂𝗯
↳ Fᴏʀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟs — ᴜsᴇʀs sᴜʙᴍɪᴛ ᴀ
   ᴊᴏɪɴ-ʀᴇǫᴜᴇsᴛ ᴀɴᴅ ᴀʀᴇ ᴛʀᴇᴀᴛᴇᴅ ᴀs ᴍᴇᴍʙᴇʀs
   ᴏɴᴄᴇ ᴛʜᴇ ʀᴇǫᴜᴇsᴛ ɪs sᴇɴᴛ.

🗑 𝗔𝘂𝘁𝗼 𝗗𝗲𝗹𝗲𝘁𝗲
↳ Fɪʟᴇs ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴀғᴛᴇʀ ᴀ ᴄᴜsᴛᴏᴍ ᴛɪᴍᴇʀ.
   Usᴇʀs ʀᴇᴄᴇɪᴠᴇ ᴀ ᴡᴀʀɴɪɴɢ ᴡɪᴛʜ ᴀ ʀᴇ-ᴅᴏᴡɴʟᴏᴀᴅ
   ʙᴜᴛᴛᴏɴ ᴀᴀғᴛᴇʀ ᴅᴇʟᴇᴛɪᴏɴ.

🔒 𝗣𝗿𝗼𝘁𝗲𝗰𝘁 𝗖𝗼𝗻𝘁𝗲𝗻𝘁
↳ Fɪʟᴇs ᴄᴀɴɴᴏᴛ ʙᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴏʀ sᴀᴠᴇᴅ ʙʏ
   ᴜsᴇʀs, ᴘʀᴏᴛᴇᴄᴛɪɴɢ ʏᴏᴜʀ ᴄᴏɴᴛᴇɴᴛ.

🫥 𝗛𝗶𝗱𝗲 𝗖𝗮𝗽𝘁𝗶𝗼𝗻
↳ Sᴛʀɪᴘs ᴄᴀᴘᴛɪᴏɴs ғʀᴏᴍ ᴅᴏᴄᴜᴍᴇɴᴛs ᴀɴᴅ
   ᴀᴜᴅɪᴏs ʙᴇғᴏʀᴇ ᴅᴇʟɪᴠᴇʀɪɴɢ ᴛᴏ ᴜsᴇʀs.

🔘 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗕𝘂𝘁𝘁𝗼𝗻
↳ Aᴛᴛᴀᴄʜ ᴀ ᴄᴜsᴛᴏᴍ ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴ (ᴡɪᴛʜ
   ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ) ᴛᴏ ᴇᴠᴇʀʏ ᴅᴇʟɪᴠᴇʀᴇᴅ ғɪʟᴇ.

🎭 𝗠𝗮𝘀𝗸 𝗕𝘂𝘁𝘁𝗼𝗻
↳ Sʜᴏᴡ ᴀ ᴄᴜsᴛᴏᴍ ʙᴜᴛᴛᴏɴ ɪɴ ᴛʜᴇ ғᴏʀᴄᴇ-sᴜʙ
   sᴄʀᴇᴇɴ, ʀᴇᴅɪʀᴇᴄᴛɪɴɢ ᴜsᴇʀs ᴛᴏ ᴀɴʏ ᴜʀʟ.

⏱ 𝗜𝗻𝘃𝗶𝘁𝗲 𝗟𝗶𝗻𝗸 𝗘𝘅𝗽𝗶𝗿𝘆
↳ Gᴇɴᴇʀᴀᴛᴇ ᴛɪᴍᴇ-ʟɪᴍɪᴛᴇᴅ ɪɴᴠɪᴛᴇ ʟɪɴᴋs. Lɪɴᴋs
   ᴀʀᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʀᴏᴛᴀᴛᴇᴅ ᴀɴᴅ ᴄᴀᴄʜᴇᴅ.

📢 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁
↳ Sᴇɴᴅ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛʏᴘᴇ (ᴛᴇxᴛ, ᴘʜᴏᴛᴏ,
   ᴠɪᴅᴇᴏ ᴇᴛᴄ.) ᴛᴏ ᴀʟʟ ᴜsᴇʀs ᴡɪᴛʜ ᴀ ʟɪᴠᴇ
   ᴘʀᴏɢʀᴇss ʙᴀʀ. Sɪʟᴇɴᴛ ᴍᴏᴅᴇ ᴀʟsᴏ ᴀᴠᴀɪʟᴀʙʟᴇ.

🔗 𝗙𝗼𝗿𝗺𝗮𝘁𝘁𝗲𝗱 𝗟𝗶𝗻𝗸 (/flink)
↳ Gᴇɴᴇʀᴀᴛᴇ ᴍᴜʟᴛɪᴘʟᴇ ǫᴜᴀʟɪᴛʏ ʟɪɴᴋs ᴡɪᴛʜ
   ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴs ɪɴ ᴀ ᴄᴜsᴛᴏᴍ ғᴏʀᴍᴀᴛ
   (360P, 480P, 720P, 1080P, 4K ᴇᴛᴄ.)

🚫 𝗕𝗮𝗻 𝗦𝘆𝘀𝘁𝗲𝗺
↳ Bᴀɴ ᴜsᴇʀs ᴛᴏ ʙʟᴏᴄᴋ ᴛʜᴇᴍ ғʀᴏᴍ ɪɴᴛᴇʀᴀᴄᴛɪɴɢ
   ᴡɪᴛʜ ᴛʜᴇ ʙᴏᴛ ᴄᴏᴍᴘʟᴇᴛᴇʟʏ.

👥 𝗔𝗱𝗺𝗶𝗻 𝗦𝘆𝘀𝘁𝗲𝗺
↳ Gʀᴀɴᴛ ᴛʀᴜsᴛᴇᴅ ᴜsᴇʀs ᴀᴅᴍɪɴ ᴀᴄᴄᴇss ᴛᴏ
   ʜᴇʟᴘ ᴍᴀɴᴀɢᴇ ᴛʜᴇ ʙᴏᴛ ᴀɴᴅ ɪᴛs ᴜsᴇʀs.
</blockquote></b>"""


HELP_FSUB_CMDS = """<b>📡 𝗙𝗢𝗥𝗖𝗘 𝗦𝗨𝗕 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦

<blockquote expandable>
📋 <b>/forcesub</b>
↳ Vɪᴇᴡ ᴀʟʟ ғᴏʀᴄᴇ-sᴜʙ ʀᴇʟᴀᴛᴇᴅ ᴄᴏᴍᴍᴀɴᴅs.

📋 <b>/fsub_chnl</b> (ᴀᴅᴍɪɴs)
↳ Lɪsᴛ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ғᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟs ᴡɪᴛʜ
   ᴛʜᴇɪʀ ɴᴀᴍᴇs ᴀɴᴅ IDs.

➕ <b>/add_fsub</b> [channel_id(s)] (ᴏᴡɴᴇʀ)
↳ Aᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴄʜᴀɴɴᴇʟ IDs.
   Tʜᴇ ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ɪɴ ᴇᴀᴄʜ ᴄʜᴀɴɴᴇʟ.
   ᴇxᴀᴍᴘʟᴇ: <code>/add_fsub -100xxxxxxxxxx -100yyyyyyyyyy</code>

➖ <b>/del_fsub</b> [channel_id(s) | all] (ᴏᴡɴᴇʀ)
↳ Rᴇᴍᴏᴠᴇ sᴘᴇᴄɪғɪᴄ ᴄʜᴀɴɴᴇʟs ᴏʀ ᴄʟᴇᴀʀ ᴀʟʟ.
   ᴇxᴀᴍᴘʟᴇ: <code>/del_fsub all</code>

📢 <b>/req_fsub</b>
↳ Tᴏɢɢʟᴇ Rᴇǫᴜᴇsᴛ Fᴏʀᴄᴇ Sᴜʙ ᴍᴏᴅᴇ ON/OFF.
   Aʟsᴏ ᴀᴄᴄᴇss:
   • Lɪsᴛ ᴏғ ʀᴇǫᴜᴇsᴛ ᴄʜᴀɴɴᴇʟs & ᴛʜᴇɪʀ ᴜsᴇʀs
   • Cʟᴇᴀʀ ᴜsᴇʀ ᴅᴀᴛᴀ ᴘᴇʀ ᴄʜᴀɴɴᴇʟ
   • Dᴇʟᴇᴛᴇ ᴄʜᴀɴɴᴇʟ ᴅᴀᴛᴀ ᴇɴᴛɪʀᴇʟʏ
   • Rᴇᴠᴏᴋᴇ & ᴄʟᴇᴀʀ sᴛᴏʀᴇᴅ ʀᴇǫᴜᴇsᴛ ʟɪɴᴋs
</blockquote></b>"""


HELP_USER_CMDS = """<b>👤 𝗨𝗦𝗘𝗥 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦

<blockquote expandable>
📋 <b>/admin_list</b> (ᴏᴡɴᴇʀ)
↳ Vɪᴇᴡ ᴀʟʟ ᴄᴜʀʀᴇɴᴛ ʙᴏᴛ ᴀᴅᴍɪɴs.

➕ <b>/add_admins</b> [user_id(s)] (ᴏᴡɴᴇʀ)
↳ Aᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀs ᴀs ʙᴏᴛ ᴀᴅᴍɪɴs.
   Aᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴀʟʟ ᴀᴅᴍɪɴ-ʟᴇᴠᴇʟ ᴄᴏᴍᴍᴀɴᴅs.

➖ <b>/del_admins</b> [user_id(s) | all] (ᴏᴡɴᴇʀ)
↳ Rᴇᴠᴏᴋᴇ ᴀᴅᴍɪɴ ᴘʀɪᴠɪʟᴇɢᴇs ғʀᴏᴍ ᴜsᴇʀ(s).

📋 <b>/banuser_list</b> (ᴀᴅᴍɪɴs)
↳ Vɪᴇᴡ ᴀʟʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀs ᴡɪᴛʜ ᴛʜᴇɪʀ ɴᴀᴍᴇs.

🚫 <b>/add_banuser</b> [user_id(s)] (ᴀᴅᴍɪɴs)
↳ Bᴀɴ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀs. Bᴀɴɴᴇᴅ ᴜsᴇʀs
   ᴄᴀɴɴᴏᴛ ᴜsᴇ /sᴛᴀʀᴛ ᴏʀ /ʜᴇʟᴘ.

✅ <b>/del_banuser</b> [user_id(s) | all] (ᴀᴅᴍɪɴs)
↳ Uɴʙᴀɴ ᴜsᴇʀ(s) ᴏʀ ᴄʟᴇᴀʀ ᴛʜᴇ ᴇɴᴛɪʀᴇ ʙᴀɴ ʟɪsᴛ.

📋 <b>/users</b>
↳ Vɪᴇᴡ ᴀʟʟ ᴜsᴇʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴄᴏᴍᴍᴀɴᴅs.
</blockquote></b>"""


# ══════════════════════════════════════════════════════════════════
#                      KEYBOARD BUILDERS
# ══════════════════════════════════════════════════════════════════

def main_help_keyboard(user_id: int, is_owner: bool, is_adm: bool):
    buttons = [
        [
            InlineKeyboardButton("🤖 Aᴅᴍɪɴ Cᴍᴅs", callback_data="help:admin"),
            InlineKeyboardButton("✨ Fᴇᴀᴛᴜʀᴇs",    callback_data="help:features"),
        ],
        [
            InlineKeyboardButton("📡 Fᴏʀᴄᴇ Sᴜʙ",   callback_data="help:fsub"),
            InlineKeyboardButton("👤 Usᴇʀ Mɢᴍᴛ",   callback_data="help:users"),
        ],
        [
            InlineKeyboardButton("⚙️ Sᴇᴛᴛɪɴɢs",    callback_data="help:settings"),
        ],
    ]
    if is_owner:
        buttons.append([InlineKeyboardButton("👑 Oᴡɴᴇʀ Cᴍᴅs", callback_data="help:owner")])
    buttons.append([InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")])
    return InlineKeyboardMarkup(buttons)


def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="help:main"),
         InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")]
    ])


# ══════════════════════════════════════════════════════════════════
#                        /help COMMAND
# ══════════════════════════════════════════════════════════════════

@Bot.on_message(filters.command('help') & filters.private & ~banUser)
async def help_command(client: Client, message: Message):
    await message.reply_chat_action(ChatAction.UPLOAD_PHOTO)

    user_id  = message.from_user.id
    is_owner = (user_id == OWNER_ID)
    is_adm   = is_owner or await ocean.admin_exist(user_id)

    await message.reply_photo(
        photo   = random.choice(PICS),
        caption = HELP_PANEL_MAIN.format(
            first    = message.from_user.first_name,
            mention  = message.from_user.mention,
        ),
        reply_markup          = main_help_keyboard(user_id, is_owner, is_adm),
        message_effect_id     = 5046509860389126442,   # 🎉
        disable_web_page_preview = True
    )
    try:
        await message.delete()
    except:
        pass


# ══════════════════════════════════════════════════════════════════
#                     CALLBACK QUERY HANDLER
# ══════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "help:admin":    (HELP_ADMIN_CMDS,  "https://graph.org//file/10f310dd6a7cb56ad7c0b.jpg"),
    "help:owner":    (HELP_OWNER_CMDS,  "https://graph.org//file/10f310dd6a7cb56ad7c0b.jpg"),
    "help:settings": (HELP_SETTINGS,    "https://graph.org//file/10f310dd6a7cb56ad7c0b.jpg"),
    "help:features": (HELP_FEATURES,    "https://graph.org//file/10f310dd6a7cb56ad7c0b.jpg"),
    "help:fsub":     (HELP_FSUB_CMDS,   "https://graph.org//file/10f310dd6a7cb56ad7c0b.jpg"),
    "help:users":    (HELP_USER_CMDS,   "https://graph.org//file/10f310dd6a7cb56ad7c0b.jpg"),
}

@Bot.on_callback_query(filters.regex(r'^help:'))
async def help_callback(client: Bot, query: CallbackQuery):
    data    = query.data
    user_id = query.from_user.id

    # ── owner-only guard ──────────────────────────────────────────
    if data == "help:owner" and user_id != OWNER_ID:
        return await query.answer("❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴛʜᴇ Oᴡɴᴇʀ !", show_alert=True)

    # ── main panel (back button) ──────────────────────────────────
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

    # ── section pages ─────────────────────────────────────────────
    if data in SECTION_MAP:
        caption, photo = SECTION_MAP[data]
        try:
            await query.edit_message_media(
                InputMediaPhoto(media=photo, caption=caption),
                reply_markup = back_keyboard()
            )
        except Exception:
            # fallback: edit text only if media edit fails
            await query.edit_message_caption(
                caption      = caption,
                reply_markup = back_keyboard()
            )
        return await query.answer()

    await query.answer()