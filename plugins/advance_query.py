import re
import random
from bot import Bot
from plugins.FORMATS import *
from config import OWNER_ID, PICS
from helper_func import S
from pyrogram.enums import ChatAction
from plugins.autoDelete import convert_time
from database.database import ocean
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, InputMediaPhoto,
    ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from pyrogram import Client, filters

try:
    from .utils import Bot_config, Message_config
    ADMIN_USER    = Bot_config.is_admin
    ENCODE_MSG    = Message_config.encode
    GET_MESSAGE_ID = Message_config.get_message_id
except ImportError:
    try:
        from helper_func import is_admin, encode, get_message_id
        ADMIN_USER    = is_admin
        ENCODE_MSG    = encode
        GET_MESSAGE_ID = get_message_id
    except ImportError:
        from helper_func import encode, get_message_id
        from config import ADMINS
        ADMIN_USER    = filters.user(ADMINS)
        ENCODE_MSG    = encode
        GET_MESSAGE_ID = get_message_id

# ── Constants ─────────────────────────────────────────────────────────────────
EXAMPLES = S("""Examples:
<blockquote expandable><code>360P = 2, 480P = 2, 720P = 2
1080P = 2, HDRIP = 1, 4K = 1</code>

<code>360P = 1, 480P = 1, 720P = 1
1080P = 1</code>

<code>360P = 1, 480P = 1, 720P = 1
1080P = 1, HDRIP = 1, 4K = 1</code>

<code>480P = 2, 720P = 2, 1080P = 2
HDRIP = 1, 4K = 1</code></blockquote>""")


def make_inline_button(text: str) -> ReplyKeyboardMarkup:
    inline_buttons = []
    for line in text.splitlines():
        tmp_buttons = []
        for button in line.split(' | '):
            try:
                button_txt, button_link = button.split(' - ')
            except Exception as e:
                print(f"Exception in make_inline_button: {e}")
                return None
            tmp_buttons.append(InlineKeyboardButton(text=button_txt, url=button_link))
        inline_buttons.append(tmp_buttons)
    return InlineKeyboardMarkup(inline_buttons)


async def del_msg(*msgs):
    for msg in msgs:
        try:
            await msg.delete()
        except Exception:
            pass


closeButton   = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])
cancelKeyboard = ReplyKeyboardMarkup([['CANCEL']], one_time_keyboard=True, resize_keyboard=True)

format_data = {}


async def format_status_msg(message, user_id: int) -> str:
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(S('🔗 Set Format'), callback_data='flink:change_format')],
        [InlineKeyboardButton(S('⚡ Start Process'), callback_data='flink:start')],
        [InlineKeyboardButton('🔄', callback_data='flink:status'), InlineKeyboardButton(S("✖️"), callback_data="close")]
    ])
    link_format = format_data.get(user_id, S('--- None ---'))
    await message.edit(
        text=(f"<b>🔗 ꜰᴏʀᴍᴀᴛᴛᴇᴅ ʟɪɴᴋ:\n\nᴄᴜʀʀᴇɴᴛ ꜰᴏʀᴍᴀᴛ\n<blockquote><code>{link_format}</code></blockquote></b>"),
        reply_markup=buttons
    )


@Bot.on_message(filters.command('flink') & filters.private & ADMIN_USER)
async def handle_formated_link(client, message):
    user_id = message.from_user.id
    wait_msg = await message.reply(S("<b><i>Processing...</i></b>"), quote=True)
    await format_status_msg(wait_msg, user_id)


async def fileSettings(getfunc, setfunc=None, delfunc=False):
    btn_mode, txt_mode, pic_mode = '❌', off_txt, off_pic
    del_btn_mode = S('Enable ✅')
    try:
        if not setfunc:
            if await getfunc():
                txt_mode = on_txt
                btn_mode = '✅'
                del_btn_mode = S('Disable ❌')
            return txt_mode, (del_btn_mode if delfunc else btn_mode)
        else:
            if await getfunc():
                await setfunc(False)
            else:
                await setfunc(True)
                pic_mode, txt_mode = on_pic, on_txt
                btn_mode = '✅'
                del_btn_mode = S('Disable ❌')
            return pic_mode, txt_mode, (del_btn_mode if delfunc else btn_mode)
    except Exception as e:
        print(f"Error in fileSettings: {e}")


def buttonStatus(pc_data: str, hc_data: str, cb_data: str) -> list:
    return [
        [
            InlineKeyboardButton(S(f'Protect Content: {pc_data}'), callback_data='pc'),
            InlineKeyboardButton(S(f'Hide Caption: {hc_data}'), callback_data='hc')
        ],
        [
            InlineKeyboardButton(S(f'Channel Button: {cb_data}'), callback_data='cb'),
            InlineKeyboardButton(S(f'Set Button ➪'), callback_data='setcb')
        ],
        [
            InlineKeyboardButton(S('🔄 Refresh'), callback_data='files_cmd'),
            InlineKeyboardButton(S('Close ✖️'), callback_data='close')
        ],
    ]


async def authoUser(query, id, owner_only=False):
    if not owner_only:
        if not any([id == OWNER_ID, await ocean.admin_exist(id)]):
            await query.answer(S("❌ Access restricted to admins only."), show_alert=True)
            return False
        return True
    else:
        if id != OWNER_ID:
            await query.answer(S("❌ Access restricted to the owner only."), show_alert=True)
            return False
        return True


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except Exception:
            pass

    elif data == "about":
        user = await client.get_users(OWNER_ID)
        user_link = f"https://t.me/{user.username}" if user.username else f"tg://openmessage?user_id={OWNER_ID}"
        ownername = f"<a href={user_link}>{user.first_name}</a>" if user.first_name else f"<a href={user_link}>No name</a>"
        await query.edit_message_media(
            InputMediaPhoto(
                "https://i.ibb.co/KpjQJbpQ/about.jpg",
                ABOUT_TXT.format(botname=client.name, ownername=ownername)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(S('⬅️ Back'), callback_data='start'), InlineKeyboardButton(S('Close ✖️'), callback_data='close')]
            ]),
        )

    elif data == "setting":
        await query.edit_message_media(InputMediaPhoto(random.choice(PICS), S("<b>Hold on...\n\n<i>🔄 Loading all settings...</i></b>")))
        try:
            total_fsub    = len(await ocean.get_all_channels())
            total_admin   = len(await ocean.get_all_admins())
            total_ban     = len(await ocean.get_ban_users())
            autodel_mode  = S('Enabled')  if await ocean.get_auto_delete()       else S('Disabled')
            protect_content = S('Enabled') if await ocean.get_protect_content()   else S('Disabled')
            hide_caption  = S('Enabled')  if await ocean.get_hide_caption()       else S('Disabled')
            chnl_butn     = S('Enabled')  if await ocean.get_channel_button()     else S('Disabled')
            reqfsub       = S('Enabled')  if await ocean.get_request_forcesub()   else S('Disabled')

            await query.edit_message_media(
                InputMediaPhoto(
                    random.choice(PICS),
                    SETTING_TXT.format(
                        total_fsub=total_fsub, total_admin=total_admin, total_ban=total_ban,
                        autodel_mode=autodel_mode, protect_content=protect_content,
                        hide_caption=hide_caption, chnl_butn=chnl_butn, reqfsub=reqfsub
                    )
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(S('⬅️ Back'), callback_data='start'), InlineKeyboardButton(S('Close ✖️'), callback_data='close')]
                ]),
            )
        except Exception as e:
            print(f"Error on callback 'setting': {e}")

    elif data == "start":
        await query.edit_message_media(
            InputMediaPhoto(
                random.choice(PICS),
                START_MSG.format(
                    first=query.from_user.first_name,
                    last=query.from_user.last_name,
                    username=None if not query.from_user.username else '@' + query.from_user.username,
                    mention=query.from_user.mention,
                    id=query.from_user.id
                )
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(S('🤖 About Me'), callback_data='about'), InlineKeyboardButton(S('Settings ⚙️'), callback_data='setting')]
            ]),
        )

    elif data == "files_cmd":
        if await authoUser(query, query.from_user.id):
            await query.answer(S("♻️ Refreshing..."))
            try:
                protect_content, pcd = await fileSettings(ocean.get_protect_content)
                hide_caption, hcd    = await fileSettings(ocean.get_hide_caption)
                channel_button, cbd  = await fileSettings(ocean.get_channel_button)
                name, link           = await ocean.get_channel_button_link()
                await query.edit_message_media(
                    InputMediaPhoto(
                        files_cmd_pic,
                        FILES_CMD_TXT.format(
                            protect_content=protect_content, hide_caption=hide_caption,
                            channel_button=channel_button, name=name, link=link
                        )
                    ),
                    reply_markup=InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd)),
                )
            except Exception as e:
                print(f"Error on callback 'files_cmd': {e}")

    elif data == "pc":
        if await authoUser(query, query.from_user.id):
            await query.answer(S("♻️ Updating..."))
            try:
                pic, protect_content, pcd = await fileSettings(ocean.get_protect_content, ocean.set_protect_content)
                hide_caption, hcd         = await fileSettings(ocean.get_hide_caption)
                channel_button, cbd       = await fileSettings(ocean.get_channel_button)
                name, link                = await ocean.get_channel_button_link()
                await query.edit_message_media(
                    InputMediaPhoto(pic, FILES_CMD_TXT.format(
                        protect_content=protect_content, hide_caption=hide_caption,
                        channel_button=channel_button, name=name, link=link
                    )),
                    reply_markup=InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd))
                )
            except Exception as e:
                print(f"Error on callback 'pc': {e}")

    elif data == "hc":
        if await authoUser(query, query.from_user.id):
            await query.answer(S("♻️ Updating..."))
            try:
                protect_content, pcd      = await fileSettings(ocean.get_protect_content)
                pic, hide_caption, hcd    = await fileSettings(ocean.get_hide_caption, ocean.set_hide_caption)
                channel_button, cbd       = await fileSettings(ocean.get_channel_button)
                name, link                = await ocean.get_channel_button_link()
                await query.edit_message_media(
                    InputMediaPhoto(pic, FILES_CMD_TXT.format(
                        protect_content=protect_content, hide_caption=hide_caption,
                        channel_button=channel_button, name=name, link=link
                    )),
                    reply_markup=InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd))
                )
            except Exception as e:
                print(f"Error on callback 'hc': {e}")

    elif data == "cb":
        if await authoUser(query, query.from_user.id):
            await query.answer(S("♻️ Updating..."))
            try:
                protect_content, pcd      = await fileSettings(ocean.get_protect_content)
                hide_caption, hcd         = await fileSettings(ocean.get_hide_caption)
                pic, channel_button, cbd  = await fileSettings(ocean.get_channel_button, ocean.set_channel_button)
                name, link                = await ocean.get_channel_button_link()
                await query.edit_message_media(
                    InputMediaPhoto(pic, FILES_CMD_TXT.format(
                        protect_content=protect_content, hide_caption=hide_caption,
                        channel_button=channel_button, name=name, link=link
                    )),
                    reply_markup=InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd))
                )
            except Exception as e:
                print(f"Error on callback 'cb': {e}")

    elif data == "setcb":
        id = query.from_user.id
        if await authoUser(query, id):
            await query.answer(S("♻️ Waiting for input..."))
            try:
                button_name, button_link = await ocean.get_channel_button_link()
                set_msg = await client.ask(
                    chat_id=id,
                    text=S(f'<b>Send new button details within 1 minute to update it.\nFormat:\n<blockquote><code>Join Channel - https://t.me/btth480p</code></blockquote>\n\n<i>Preview below ⬇️</i></b>'),
                    timeout=60,
                    reply_markup=ReplyKeyboardMarkup([['CANCEL']], one_time_keyboard=True, resize_keyboard=True),
                    disable_web_page_preview=True
                )
                if set_msg.text == 'CANCEL':
                    return await set_msg.reply(S("<b><i>🆞 Cancelled.</i></b>"), reply_markup=ReplyKeyboardRemove())
                button = set_msg.text.split(' - ')
                if len(button) != 2:
                    markup = [[InlineKeyboardButton(S(f'Set Channel Button ➪'), callback_data='setcb')]]
                    return await set_msg.reply(
                        S("<b>Invalid format. Send it like:\n<blockquote><code>Join Channel - https://t.me/btth480p</code></blockquote>\n\n<i>Tap below to try again.</i></b>"),
                        reply_markup=InlineKeyboardMarkup(markup), disable_web_page_preview=True
                    )
                button_name = button[0].strip()
                button_link = button[1].strip()
                button_preview = [[InlineKeyboardButton(text=button_name, url=button_link)]]
                await set_msg.reply(
                    S("<b><i>Saved successfully ✅</i>\n<blockquote>Preview below ⬇️</blockquote></b>"),
                    reply_markup=InlineKeyboardMarkup(button_preview)
                )
                await ocean.set_channel_button_link(button_name, button_link)
            except Exception as e:
                try:
                    await set_msg.reply(S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote>"))
                    print(f"Error on callback 'setcb': {e}")
                except Exception:
                    await client.send_message(
                        id,
                        text=S("<b>Something went wrong.\n<blockquote><i>Reason: 1-minute timeout reached.</i></b></blockquote>"),
                        disable_notification=True
                    )

    elif data == 'autodel_cmd':
        if await authoUser(query, query.from_user.id, owner_only=True):
            await query.answer(S("♻️ Refreshing..."))
            try:
                timer = convert_time(await ocean.get_del_timer())
                autodel_mode, mode = await fileSettings(ocean.get_auto_delete, delfunc=True)
                await query.edit_message_media(
                    InputMediaPhoto(autodel_cmd_pic, AUTODEL_CMD_TXT.format(autodel_mode=autodel_mode, timer=timer)),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(mode, callback_data='chng_autodel'), InlineKeyboardButton(S('⏱ Set Timer'), callback_data='set_timer')],
                        [InlineKeyboardButton(S('🔄 Refresh'), callback_data='autodel_cmd'), InlineKeyboardButton(S('Close ✖️'), callback_data='close')]
                    ])
                )
            except Exception as e:
                print(f"Error on callback 'autodel_cmd': {e}")

    elif data == 'chng_autodel':
        if await authoUser(query, query.from_user.id, owner_only=True):
            await query.answer(S("♻️ Updating..."))
            try:
                timer = convert_time(await ocean.get_del_timer())
                pic, autodel_mode, mode = await fileSettings(ocean.get_auto_delete, ocean.set_auto_delete, delfunc=True)
                await query.edit_message_media(
                    InputMediaPhoto(pic, AUTODEL_CMD_TXT.format(autodel_mode=autodel_mode, timer=timer)),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(mode, callback_data='chng_autodel'), InlineKeyboardButton(S('⏱ Set Timer'), callback_data='set_timer')],
                        [InlineKeyboardButton(S('🔄 Refresh'), callback_data='autodel_cmd'), InlineKeyboardButton(S('Close ✖️'), callback_data='close')]
                    ])
                )
            except Exception as e:
                print(f"Error on callback 'chng_autodel': {e}")

    elif data == 'set_timer':
        id = query.from_user.id
        if await authoUser(query, id, owner_only=True):
            try:
                timer = convert_time(await ocean.get_del_timer())
                set_msg = await client.ask(
                    chat_id=id,
                    text=S(f'<b><blockquote>⏱ Current Timer: {timer}</blockquote>\n\nSend a number in seconds within 1 minute to update it.\n<blockquote>Example: <code>300</code>, <code>600</code>, <code>900</code></b></blockquote>'),
                    timeout=60,
                    reply_markup=ReplyKeyboardMarkup([['CANCEL']], one_time_keyboard=True, resize_keyboard=True)
                )
                if set_msg.text == 'CANCEL':
                    return await set_msg.reply(S("<b><i>🆞 Cancelled.</i></b>"), reply_markup=ReplyKeyboardRemove())
                del_timer = set_msg.text.split()
                if len(del_timer) == 1 and del_timer[0].isdigit():
                    DEL_TIMER = int(del_timer[0])
                    await ocean.set_del_timer(DEL_TIMER)
                    timer = convert_time(DEL_TIMER)
                    await set_msg.reply(S(f"<b><i>Saved successfully ✅</i>\n<blockquote>⏱ New Timer: {timer}</blockquote></b>"))
                else:
                    markup = [[InlineKeyboardButton(S('⏱ Set Delete Timer'), callback_data='set_timer')]]
                    return await set_msg.reply(
                        S("<b>Please send a valid number in seconds.\n<blockquote>Example: <code>300</code>, <code>600</code>, <code>900</code></blockquote>\n\n<i>Tap below to try again.</i></b>"),
                        reply_markup=InlineKeyboardMarkup(markup)
                    )
            except Exception as e:
                try:
                    await set_msg.reply(S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote>"))
                    print(f"Error on callback 'set_timer': {e}")
                except Exception:
                    await client.send_message(
                        id,
                        text=S("<b>Something went wrong.\n<blockquote><i>Reason: 1-minute timeout reached.</i></b></blockquote>"),
                        disable_notification=True
                    )

    elif data == 'chng_req':
        if await authoUser(query, query.from_user.id, owner_only=True):
            await query.answer(S("♻️ Updating..."))
            try:
                on = off = ""
                if await ocean.get_request_forcesub():
                    await ocean.set_request_forcesub(False)
                    off = "🔴"
                    texting = off_txt
                else:
                    await ocean.set_request_forcesub(True)
                    on = "🟢"
                    texting = on_txt
                client.REQFSUB = await ocean.get_request_forcesub()
                button = [
                    [InlineKeyboardButton(f"{on} ON", "chng_req"), InlineKeyboardButton(f"{off} OFF", "chng_req")],
                    [InlineKeyboardButton(S("⚙️ More Settings"), "more_settings")]
                ]
                await query.message.edit_text(text=RFSUB_CMD_TXT.format(req_mode=texting), reply_markup=InlineKeyboardMarkup(button))
            except Exception as e:
                print(f"Error on callback 'chng_req': {e}")

    elif data == 'more_settings':
        if await authoUser(query, query.from_user.id, owner_only=True):
            try:
                await query.message.edit_text(S("<b>Hold on...\n\n<i>🔄 Loading all settings...</i></b>"))
                LISTS = S("No request force-sub channels registered.")

                REQFSUB_CHNLS = await ocean.get_reqChannel()
                if REQFSUB_CHNLS:
                    LISTS = ""
                    channel_name = S("<i>Unable to load name.</i>")
                    for CHNL in REQFSUB_CHNLS:
                        await query.message.reply_chat_action(ChatAction.TYPING)
                        try:
                            name = (await client.get_chat(CHNL)).title
                        except Exception:
                            name = None
                        channel_name = name if name else channel_name
                        user = await ocean.get_reqSent_user(CHNL)
                        channel_users = len(user) if user else 0
                        link = await ocean.get_stored_reqLink(CHNL)
                        if link:
                            channel_name = f"<a href={link}>{channel_name}</a>"
                        LISTS += S(f"Name: {channel_name}\n(ID: <code>{CHNL}</code>)\nUsers: {channel_users}\n\n")

                buttons = [
                    [InlineKeyboardButton(S("Clear Channels"), "clear_chnls"), InlineKeyboardButton(S("Clear Links"), "clear_links")],
                    [InlineKeyboardButton(S("♻️  Refresh Status  ♻️"), "more_settings")],
                    [InlineKeyboardButton(S("⬅️ Back"), "req_fsub"), InlineKeyboardButton(S("Close ✖️"), "close")]
                ]
                await query.message.reply_chat_action(ChatAction.CANCEL)
                await query.message.edit_text(
                    text=RFSUB_MS_TXT.format(reqfsub_list=LISTS.strip()),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except Exception as e:
                print(f"Error on callback 'more_settings': {e}")

    elif data == 'clear_users':
        try:
            REQFSUB_CHNLS = await ocean.get_reqChannel()
            if not REQFSUB_CHNLS:
                return await query.answer(S("No request force-sub channels found."), show_alert=True)
            await query.answer(S("♻️ Processing..."))
            REQFSUB_CHNLS = list(map(str, REQFSUB_CHNLS))
            buttons = [REQFSUB_CHNLS[i:i+2] for i in range(0, len(REQFSUB_CHNLS), 2)]
            buttons.insert(0, ['CANCEL'])
            buttons.append(['DELETE ALL CHANNELS USER'])
            user_reply = await client.ask(
                query.from_user.id, text=CLEAR_USERS_TXT,
                reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
            )
            if user_reply.text == 'CANCEL':
                return await user_reply.reply(S("<b><i>🆑 Cancelled.</i></b>"), reply_markup=ReplyKeyboardRemove())
            elif user_reply.text in REQFSUB_CHNLS:
                try:
                    await ocean.clear_reqSent_user(int(user_reply.text))
                    return await user_reply.reply(
                        S(f"<b><blockquote>✅ User data cleared for channel ID: <code>{user_reply.text}</code></blockquote></b>"),
                        reply_markup=ReplyKeyboardRemove()
                    )
                except Exception as e:
                    return await user_reply.reply(S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote>"), reply_markup=ReplyKeyboardRemove())
            elif user_reply.text == 'DELETE ALL CHANNELS USER':
                try:
                    for CHNL in REQFSUB_CHNLS:
                        await ocean.clear_reqSent_user(int(CHNL))
                    return await user_reply.reply(S("<b><blockquote>✅ User data cleared from all channel IDs.</blockquote></b>"), reply_markup=ReplyKeyboardRemove())
                except Exception as e:
                    return await user_reply.reply(S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote>"), reply_markup=ReplyKeyboardRemove())
            else:
                return await user_reply.reply(S("<b><blockquote>Invalid selection.</blockquote></b>"), reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            print(f"Error on callback 'clear_users': {e}")

    elif data == 'clear_chnls':
        try:
            REQFSUB_CHNLS = await ocean.get_reqChannel()
            if not REQFSUB_CHNLS:
                return await query.answer(S("No request force-sub channels found."), show_alert=True)
            await query.answer(S("♻️ Processing..."))
            REQFSUB_CHNLS = list(map(str, REQFSUB_CHNLS))
            buttons = [REQFSUB_CHNLS[i:i+2] for i in range(0, len(REQFSUB_CHNLS), 2)]
            buttons.insert(0, ['CANCEL'])
            buttons.append(['DELETE ALL CHANNEL IDS'])
            user_reply = await client.ask(
                query.from_user.id, text=CLEAR_CHNLS_TXT,
                reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
            )
            if user_reply.text == 'CANCEL':
                return await user_reply.reply(S("<b><i>🆑 Cancelled.</i></b>"), reply_markup=ReplyKeyboardRemove())
            elif user_reply.text in REQFSUB_CHNLS:
                try:
                    await ocean.del_reqChannel(int(user_reply.text))
                    client.CHANNEL_LIST = await ocean.get_all_channels()
                    return await user_reply.reply(
                        S(f"<b><blockquote><code>{user_reply.text}</code> channel ID removed successfully ✅</blockquote></b>"),
                        reply_markup=ReplyKeyboardRemove()
                    )
                except Exception as e:
                    return await user_reply.reply(S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote>"), reply_markup=ReplyKeyboardRemove())
            elif user_reply.text == 'DELETE ALL CHANNEL IDS':
                try:
                    for CHNL in REQFSUB_CHNLS:
                        await ocean.del_reqChannel(int(CHNL))
                    client.CHANNEL_LIST = await ocean.get_all_channels()
                    return await user_reply.reply(S("<b><blockquote>All channel IDs removed successfully ✅</blockquote></b>"), reply_markup=ReplyKeyboardRemove())
                except Exception as e:
                    return await user_reply.reply(S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote>"), reply_markup=ReplyKeyboardRemove())
            else:
                return await user_reply.reply(S("<b><blockquote>Invalid selection.</blockquote></b>"), reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            print(f"Error on callback 'clear_chnls': {e}")

    elif data == 'clear_links':
        try:
            REQFSUB_CHNLS = await ocean.get_reqLink_channels()
            if not REQFSUB_CHNLS:
                return await query.answer(S("No stored request links found."), show_alert=True)
            await query.answer(S("♻️ Processing..."))
            REQFSUB_CHNLS = list(map(str, REQFSUB_CHNLS))
            buttons = [REQFSUB_CHNLS[i:i+2] for i in range(0, len(REQFSUB_CHNLS), 2)]
            buttons.insert(0, ['CANCEL'])
            buttons.append(['DELETE ALL REQUEST LINKS'])
            user_reply = await client.ask(
                query.from_user.id, text=CLEAR_LINKS_TXT,
                reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
            )
            if user_reply.text == 'CANCEL':
                return await user_reply.reply(S("<b><i>🆑 Cancelled.</i></b>"), reply_markup=ReplyKeyboardRemove())
            elif user_reply.text in REQFSUB_CHNLS:
                channel_id = int(user_reply.text)
                try:
                    try:
                        await client.revoke_chat_invite_link(channel_id, await ocean.get_stored_reqLink(channel_id))
                    except Exception:
                        text = S("""<b>❌ Unable to revoke link.
<blockquote expandable>ID: <code>{}</code></b>
<i>Bot may not be in this channel or lacks the required admin permissions.</i></blockquote>""")
                        return await user_reply.reply(text=text.format(channel_id), reply_markup=ReplyKeyboardRemove())
                    await ocean.del_stored_reqLink(channel_id)
                    return await user_reply.reply(
                        S(f"<b><blockquote><code>{channel_id}</code> channel link removed successfully ✅</blockquote></b>"),
                        reply_markup=ReplyKeyboardRemove()
                    )
                except Exception as e:
                    return await user_reply.reply(S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote>"), reply_markup=ReplyKeyboardRemove())
            elif user_reply.text == 'DELETE ALL REQUEST LINKS':
                try:
                    result = ""
                    for CHNL in REQFSUB_CHNLS:
                        channel_id = int(CHNL)
                        try:
                            await client.revoke_chat_invite_link(channel_id, await ocean.get_stored_reqLink(channel_id))
                        except Exception:
                            result += S(f"<blockquote expandable><b><code>{channel_id}</code> Unable to revoke ❌</b>\n<i>Bot may not be in this channel or lacks admin permissions.</i></blockquote>\n")
                            continue
                        await ocean.del_stored_reqLink(channel_id)
                        result += S(f"<blockquote><b><code>{channel_id}</code> link removed ✅</b></blockquote>\n")
                    return await user_reply.reply(S(f"<b>Operation Result:</b>\n{result.strip()}"), reply_markup=ReplyKeyboardRemove())
                except Exception as e:
                    return await user_reply.reply(S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote>"), reply_markup=ReplyKeyboardRemove())
            else:
                return await user_reply.reply(S("<b><blockquote>Invalid selection.</blockquote></b>"), reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            print(f"Error on callback 'clear_links': {e}")

    elif data == 'req_fsub':
        await query.answer(S("♻️ Refreshing..."))
        try:
            on = off = ""
            if await ocean.get_request_forcesub():
                on = "🟢"
                texting = on_txt
            else:
                off = "🔴"
                texting = off_txt
            button = [
                [InlineKeyboardButton(f"{on} ON", "chng_req"), InlineKeyboardButton(f"{off} OFF", "chng_req")],
                [InlineKeyboardButton(S("⚙️ More Settings"), "more_settings")]
            ]
            await query.message.edit_text(text=RFSUB_CMD_TXT.format(req_mode=texting), reply_markup=InlineKeyboardMarkup(button))
        except Exception as e:
            print(f"Error on callback 'req_fsub': {e}")

    elif data == 'flink:status':
        user_id = query.from_user.id
        await query.message.edit_text(S("<b><i>🔄 Refreshing...</i></b>"))
        await format_status_msg(query.message, user_id)

    elif data == 'flink:change_format':
        user_id = query.from_user.id
        temp = await query.message.reply(
            S(f'<b>Send the link format with quality and message count:\n\n{EXAMPLES}</b>'),
            reply_markup=cancelKeyboard
        )
        rcv_msg = await client.listen(chat_id=user_id)
        await del_msg(temp)
        TEXT = rcv_msg.text

        if TEXT is None:
            return await rcv_msg.reply(S("<b>⚠️ Only text messages are accepted.</b>"), reply_markup=closeButton, quote=True)
        if TEXT == 'CANCEL':
            return await rcv_msg.reply(S("<b><i>🆑 Operation cancelled.</i></b>"), reply_markup=closeButton, quote=True)

        format_lines = TEXT.splitlines()
        try:
            for line in format_lines:
                for msg_data in line.split(','):
                    msg_txt, msg_len = msg_data.strip().split(' = ')
                    int(msg_len)
        except Exception as e:
            print(f"Invalid format received:\n{TEXT}\nReason: {e}")
            return await rcv_msg.reply(
                S(f"<b>⚠️ Invalid format. Please follow the structure below.\n\n{EXAMPLES}</b>"),
                reply_markup=closeButton, quote=True
            )
        else:
            format_data[user_id] = TEXT
            return await rcv_msg.reply(S("<b><i>Link format saved successfully ✅</i></b>"), reply_markup=closeButton, quote=True)

    elif data == 'flink:start':
        user_id = query.from_user.id
        link_formats = format_data.get(user_id)
        if not link_formats:
            return await query.answer(S('⚠️ Set a link format first.'), show_alert=True)

        link = client.db_channel.invite_link
        channel = f"<a href={link}>{S('db channel')}</a>" if link else S('db channel')

        while True:
            try:
                tmp = await query.message.reply(
                    text=S(f"<b><blockquote>Forward a message from {channel} (with quotes)..</blockquote>\n<blockquote>Or send the {channel} post link.</blockquote></b>"),
                    reply_markup=cancelKeyboard,
                    disable_web_page_preview=True
                )
                channel_message = await client.listen(
                    chat_id=user_id,
                    filters=(filters.forwarded | (filters.text & ~filters.forwarded))
                )
                if channel_message.text == 'CANCEL':
                    return await del_msg(channel_message, tmp)
            except Exception:
                try:
                    return await del_msg(tmp)
                except Exception:
                    return

            msg_id = await GET_MESSAGE_ID(client, channel_message)
            if msg_id:
                await del_msg(tmp)
                break
            else:
                await del_msg(tmp)
                await channel_message.reply(
                    S(f"<b>❌ Error.\n<blockquote>This post or link is not from my {channel}.</blockquote></b>"),
                    quote=True, reply_markup=closeButton, disable_web_page_preview=True
                )
                continue

        format_lines = link_formats.splitlines()
        output_txt = []

        for line in format_lines:
            qlty_links = []
            for msg_data in line.split(','):
                msg_txt, msg_len = msg_data.strip().split(' = ')
                msg_len = int(msg_len)
                if msg_len == 1:
                    msg = f'get-{msg_id * abs(client.db_channel.id)}'
                    msg_id += 1
                else:
                    first_msg = f'{msg_id * abs(client.db_channel.id)}'
                    msg_id += (msg_len - 1)
                    last_msg = f'{msg_id * abs(client.db_channel.id)}'
                    msg_id += 1
                    msg = f'get-{first_msg}-{last_msg}'
                encoded_msg = await ENCODE_MSG(msg)
                msg_link = f"https://t.me/{client.username}?start={encoded_msg}"
                qlty_links.append(f'{msg_txt} - {msg_link}')
            output_txt.append(" | ".join(qlty_links))

        final_message = '\n'.join(output_txt)
        inline_buttons = make_inline_button(final_message)
        await channel_message.reply(
            text=(f'<b>⬇️ ʜᴇʀᴇ ɪꜱ ʏᴏᴜʀ ꜰᴏʀᴍᴀᴛᴛᴇᴅ ʟɪɴᴋ:</b>\n\n<blockquote><code>{final_message}</code></blockquote>'),
            reply_markup=inline_buttons, quote=True, disable_web_page_preview=True
        )