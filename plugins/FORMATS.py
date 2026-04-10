import re
from helper_func import S

# ── Image URLs ────────────────────────────────────────────────────────────────
on_pic         = "https://telegra.ph/file/5593d624d11d92bceb48e.jpg"
off_pic        = "https://telegra.ph/file/0d9e590f62b63b51d4bf9.jpg"
files_cmd_pic  = "https://telegra.ph/file/d44f46054250a73053614.jpg"
autodel_cmd_pic = "https://telegra.ph/file/a64533814021b40057ccd.jpg"


# ── Start message ─────────────────────────────────────────────────────────────
START_MSG = S("""<blockquote><b>👋 Welcome, {first}!</blockquote>

๏ Your anime universe is just one tap away.

<blockquote>‣ Updates: <a href='https://t.me/OceanXBotz'>OceanXBotz</a>
‣ Support: <a href='https://t.me/Anime_Ocean_Official'>Animes Ocean</a></b></blockquote>""")


# ── Force-sub message ─────────────────────────────────────────────────────────
FORCE_MSG = S("""<b>🔐 Hey, {mention}

You need to join all my channels before your files can be unlocked.

<blockquote>๏ Once you have joined every channel listed below, tap "↻ Try Again" ⬇️</blockquote></b>""")


# ── Admin command summary ─────────────────────────────────────────────────────
CMD_TXT = S("""<b>🤖 CORE ADMIN COMMANDS:

<b>/batch :</b> create a batch link for multiple messages

<b>/genlink :</b> generate a link for a single post

<b>/broadcast :</b> send a message to all users

<code>/broadcast silent</code> : send without notification

<b>/status :</b> view bot statistics and uptime</b>""")


# ── Banned user message ───────────────────────────────────────────────────────
BAN_TXT = S("<b><blockquote>Access denied — you are banned. 🚫</blockquote></b>")


# ── Help text (shown to regular users via /help) ──────────────────────────────
HELP_TEXT = S("""<b>👋 Hi {mention}!

<blockquote expandable>➪ I am a private file-sharing bot that delivers anime files via encoded links for specific channels.

➪ To receive files, you must join all the required channels. Files stay locked until you do.

➪ Join the listed channels and you are all set to start receiving your anime files.

‣ /help - open this message again</blockquote>
<b><i>◈ Still stuck? Reach out to the person or group linked below.</i></b></b>""")


# ── About text ────────────────────────────────────────────────────────────────
ABOUT_TXT = S("""<b>• Hosted by: @OceanXBotz</b>""")


# ── Settings overview ─────────────────────────────────────────────────────────
SETTING_TXT = S("""<b>⚙️ CURRENT CONFIGURATION</b>
<blockquote expandable>◈ Force-Sub Channels:  <b>{total_fsub}</b>
◈ Total Admins:  <b>{total_admin}</b>
◈ Banned Users:  <b>{total_ban}</b>
◈ Auto-Delete Mode:  <b>{autodel_mode}</b>
◈ Protect Content:  <b>{protect_content}</b>
◈ Hide Caption:  <b>{hide_caption}</b>
◈ Channel Button:  <b>{chnl_butn}</b>
◈ Request FSub Mode: <b>{reqfsub}</b></blockquote>""")


# ── On / Off labels ───────────────────────────────────────────────────────────
on_txt  = S("Enabled ✅")
off_txt = S("Disabled ❌")


# ── File settings panel ───────────────────────────────────────────────────────
FILES_CMD_TXT = S("""<b>📁 FILE SETTINGS ⚙️

<blockquote expandable>🔒 Protect Content: {protect_content}
🫥 Hide Caption: {hide_caption}
🔘 Channel Button: {channel_button}</b>

◈ Button Name: {name}
◈ Button Link: {link}</blockquote>

<b>Use the buttons below to adjust these settings.</b>""")


# ── Auto-delete settings panel ────────────────────────────────────────────────
AUTODEL_CMD_TXT = S("""<b>🗑 AUTO-DELETE SETTINGS ⚙️

<blockquote>🗑 Auto-Delete Mode: {autodel_mode}</blockquote>
<blockquote>⏱ Delete Timer: {timer}</blockquote>

Use the buttons below to update these settings.</b>""")


# ── Force-sub commands (short list) ──────────────────────────────────────────
FSUB_CMD_TXT = S("""<b>📡 FORCE-SUB COMMANDS:

/fsub_chnl : list active force-sub channels (admins)

/add_fsub : add one or more force-sub channels (owner)

/del_fsub : remove one or more force-sub channels (owner)</b>""")


# ── User management commands (short list) ─────────────────────────────────────
USER_CMD_TXT = S("""<b>👤 USER MANAGEMENT COMMANDS:

/admin_list : view the admin list (owner)

/add_admins : grant admin access to one or more user IDs (owner)

/del_admins : revoke admin access from one or more user IDs (owner)

/banuser_list : view the banned users list (admins)

/add_banuser : ban one or more user IDs (admins)

/del_banuser : unban one or more user IDs (admins)</b>""")


# ── Request FSub settings panel ───────────────────────────────────────────────
RFSUB_CMD_TXT = S("""<b>🚦 REQUEST FSUB SETTINGS

<blockquote><b>📢 Request FSub Mode: {req_mode}</b></blockquote>

Use the buttons below to toggle this setting.</b>""")


# ── Request FSub detail panel ─────────────────────────────────────────────────
RFSUB_MS_TXT = S("""<b>🚥 REQUEST FSUB CHANNEL LIST

<blockquote expandable>{reqfsub_list}</blockquote>
Use the buttons below to manage these entries.</b>""")


# ── Clear users explanation ───────────────────────────────────────────────────
CLEAR_USERS_TXT = S("""<blockquote expandable><b>What does "Clear Users" do?</b>

➪ It wipes all stored user data for a selected request force-sub channel ID.

➪ Only the user data is removed — the channel itself stays registered.</blockquote>

<b><i>Pick the channel ID to clear user data from:</i></b>""")


# ── Clear channels explanation ────────────────────────────────────────────────
CLEAR_CHNLS_TXT = S("""<blockquote expandable><b>What does "Clear Channels" do?</b>

➪ It deletes all user data and removes the request force-sub channel ID from the database entirely.

➪ If user data exists, it gets wiped along with the channel ID.</blockquote>

<b><i>Select the channel ID to remove completely:</i></b>""")


# ── Clear links explanation ───────────────────────────────────────────────────
CLEAR_LINKS_TXT = S("""<blockquote expandable><b>What does "Clear Links" do?</b>

➪ It deletes stored request links for a chosen channel from the database and revokes them from that channel.

➪ Even if channel data was cleared, request links may still be stored — this removes those too.

➪ Once cleared, those links become invalid and cannot be reused.

➪ If the channel is re-added as a request force-sub channel later, the bot will generate a fresh link.

<b>⚠️ Note:</b>
‣ The bot must be an admin in that channel with the right permissions for this to work.
‣ If the bot is not in the channel or lacks admin rights, this action will fail.</blockquote>

<b><i>Choose the channel ID to revoke its request link:</i></b>""")