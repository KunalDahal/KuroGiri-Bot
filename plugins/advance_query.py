import random
from bot import Bot
from plugins.FORMATS import *
from config import OWNER_ID, PICS
from pyrogram.enums import ChatAction
from plugins.autoDelete import convert_time
from database.database import ocean
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ReplyKeyboardMarkup, ReplyKeyboardRemove

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from bot import Bot

try:
    from .utils import Bot_config, Message_config 

    ADMIN_USER = Bot_config.is_admin
    ENCODE_MSG = Message_config.encode
    GET_MESSAGE_ID = Message_config.get_message_id

except ImportError:
    try:
        from helper_func import is_admin, encode, get_message_id

        ADMIN_USER = is_admin
        ENCODE_MSG = encode
        GET_MESSAGE_ID = get_message_id

    except ImportError:
        from helper_func import encode, get_message_id 
        from config import ADMINS 

        ADMIN_USER = filters.user(ADMINS)
        ENCODE_MSG = encode
        GET_MESSAGE_ID = get_message_id
    



EXAMPLES = """Exᴀᴍᴘʟᴇs: 
<blockquote expandable><code>360P = 2, 480P = 2, 720P = 2
1080P = 2, HDRIP = 1, 4K = 1</code>

<code>360P = 1, 480P = 1, 720P = 1
1080P = 1</code>
                                      
<code>360P = 1, 480P = 1, 720P = 1
1080P = 1, HDRIP = 1, 4K = 1</code>  

<code>480P = 2, 720P = 2, 1080P = 2 
HDRIP = 1, 4K = 1</code></blockquote>"""


def make_inline_button(text:str) -> ReplyKeyboardMarkup:
    inline_buttons = []
    button_lines = text.splitlines()

    for line in button_lines:
        tmp_buttons = []
        buttons_nums = line.split(' | ')

        for button in buttons_nums:
            try:
                button_txt,  button_link = button.split(' - ') 
            except Exception as e:
                print(f"! Exception in function (make_inline_button): {e}")
                return None
            
            tmp_buttons.append(InlineKeyboardButton(text=button_txt, url=button_link))

        inline_buttons.append(tmp_buttons)
    
    return InlineKeyboardMarkup(inline_buttons)

async def del_msg(*msgs):
    for msg in msgs:
        try: await msg.delete()
        except: pass

closeButton = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
cancelKeyboard = ReplyKeyboardMarkup([['CANCEL']], one_time_keyboard=True, resize_keyboard=True)

format_data = {}

async def format_status_msg(message, user_id: int) -> str:
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('🔗 sᴇᴛ ғᴏʀᴍᴀᴛ', callback_data='flink:change_format')
            ],
            [
                InlineKeyboardButton('⚡️ sᴛᴀʀᴛ ᴘʀᴏᴄᴇss', callback_data='flink:start')
            ],
            [
                InlineKeyboardButton('🔄', callback_data='flink:status'),
                InlineKeyboardButton("✖️", callback_data = "close")
            ]
        ]
    )

    link_format = format_data.get(user_id, '--- Nᴏɴᴇ ---')

    await message.edit(
        text=f"<b>🔗 𝗙𝗢𝗥𝗠𝗔𝗧𝗘𝗗 𝗟𝗜𝗡𝗞 :\n\n◈ Cᴜʀʀᴇɴᴛ Fᴏʀᴍᴀᴛ\n<blockquote><code>{link_format}</code></blockquote></b>",
        reply_markup=buttons
    )



@Bot.on_message(filters.command('flink') & filters.private & ADMIN_USER)
async def handle_formated_link(client, message):
    user_id = message.from_user.id
    wait_msg = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)

    await format_status_msg(wait_msg, user_id)


async def fileSettings(getfunc, setfunc=None, delfunc=False) :
    btn_mode, txt_mode, pic_mode = '❌', off_txt, off_pic
    del_btn_mode = 'Eɴᴀʙʟᴇ Mᴏᴅᴇ ✅'
    try:
        if not setfunc:
            if await getfunc():
                txt_mode = on_txt    
                btn_mode = '✅'
                del_btn_mode = 'Dɪsᴀʙʟᴇ Mᴏᴅᴇ ❌'
        
            return txt_mode, (del_btn_mode if delfunc else btn_mode)
            
        else:
            if await getfunc():
                await setfunc(False)
            else:
                await setfunc(True)
                pic_mode, txt_mode = on_pic, on_txt
                btn_mode = '✅'
                del_btn_mode = 'Dɪsᴀʙʟᴇ Mᴏᴅᴇ ❌'
                
            return pic_mode, txt_mode, (del_btn_mode if delfunc else btn_mode)
            
    except Exception as e:
        print(f"Error occured at [fileSettings(getfunc, setfunc=None, delfunc=False)] : {e}")

def buttonStatus(pc_data: str, hc_data: str, cb_data: str) -> list:
    button = [
        [
            InlineKeyboardButton(f'Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ: {pc_data}', callback_data='pc'),
            InlineKeyboardButton(f'Hɪᴅᴇ Cᴀᴘᴛɪᴏɴ: {hc_data}', callback_data='hc')
        ],
        [
            InlineKeyboardButton(f'Cʜᴀɴɴᴇʟ Bᴜᴛᴛᴏɴ: {cb_data}', callback_data='cb'), 
            InlineKeyboardButton(f'◈ Sᴇᴛ Bᴜᴛᴛᴏɴ ➪', callback_data='setcb')
        ],
        [
            InlineKeyboardButton('🔄 Rᴇғʀᴇsʜ', callback_data='files_cmd'), 
            InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')
        ],
    ]
    return button

async def authoUser(query, id, owner_only=False):
    if not owner_only:
        if not any([id == OWNER_ID, await ocean.admin_exist(id)]):
            await query.answer("❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ Aᴅᴍɪɴ !", show_alert=True)
            return False
        return True
    else:
        if id != OWNER_ID:
            await query.answer("❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ Oᴡɴᴇʀ !", show_alert=True)
            return False
        return True

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data        
    if data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
            
    elif data == "about":
        user = await client.get_users(OWNER_ID)
        user_link = f"https://t.me/{user.username}" if user.username else f"tg://openmessage?user_id={OWNER_ID}" 
        ownername = f"<a href={user_link}>{user.first_name}</a>" if user.first_name else f"<a href={user_link}>no name !</a>"
        await query.edit_message_media(
            InputMediaPhoto("https://i.ibb.co/7JPjfwHm/x.jpg", 
                            ABOUT_TXT.format(
                                botname = client.name,
                                ownername = ownername, 
                            )
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('⬅️ Bᴀᴄᴋ', callback_data='start'), InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')]
            ]),
        )
        
    elif data == "setting":
        await query.edit_message_media(InputMediaPhoto(random.choice(PICS), "<b>Pʟᴇᴀsᴇ wᴀɪᴛ !\n\n<i>🔄 Rᴇᴛʀɪᴇᴠɪɴɢ ᴀʟʟ Sᴇᴛᴛɪɴɢs...</i></b>"))
        try:
            total_fsub = len(await ocean.get_all_channels())
            total_admin = len(await ocean.get_all_admins())
            total_ban = len(await ocean.get_ban_users())
            autodel_mode = 'Eɴᴀʙʟᴇᴅ' if await ocean.get_auto_delete() else 'Dɪsᴀʙʟᴇᴅ'
            protect_content = 'Eɴᴀʙʟᴇᴅ' if await ocean.get_protect_content() else 'Dɪsᴀʙʟᴇᴅ'
            hide_caption = 'Eɴᴀʙʟᴇᴅ' if await ocean.get_hide_caption() else 'Dɪsᴀʙʟᴇᴅ'
            chnl_butn = 'Eɴᴀʙʟᴇᴅ' if await ocean.get_channel_button() else 'Dɪsᴀʙʟᴇᴅ'
            reqfsub = 'Eɴᴀʙʟᴇᴅ' if await ocean.get_request_forcesub() else 'Dɪsᴀʙʟᴇᴅ'
            
            await query.edit_message_media(
                InputMediaPhoto(random.choice(PICS),
                                SETTING_TXT.format(
                                    total_fsub = total_fsub,
                                    total_admin = total_admin,
                                    total_ban = total_ban,
                                    autodel_mode = autodel_mode,
                                    protect_content = protect_content,
                                    hide_caption = hide_caption,
                                    chnl_butn = chnl_butn,
                                    reqfsub = reqfsub
                                )
                ),
                reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('⬅️ Bᴀᴄᴋ', callback_data='start'), InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')]
                ]),
            )
        except Exception as e:
            print(f"! Error Occured on callback data = 'setting' : {e}")
        
    elif data == "start":
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), 
                            START_MSG.format(
                                first = query.from_user.first_name,
                                last = query.from_user.last_name,
                                username = None if not query.from_user.username else '@' + query.from_user.username,
                                mention = query.from_user.mention,
                                id = query.from_user.id
                            )
            ),
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton('🤖 Aʙᴏᴜᴛ ᴍᴇ', callback_data='about'), InlineKeyboardButton('Sᴇᴛᴛɪɴɢs ⚙️', callback_data='setting')]
            ]),
        )
        
    elif data == "files_cmd":
        if await authoUser(query, query.from_user.id) : 
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....") 
                
            try:
                protect_content, pcd = await fileSettings(ocean.get_protect_content)
                hide_caption, hcd = await fileSettings(ocean.get_hide_caption)
                channel_button, cbd = await fileSettings(ocean.get_channel_button)
                name, link = await ocean.get_channel_button_link()
                
                await query.edit_message_media(
                    InputMediaPhoto(files_cmd_pic,
                                    FILES_CMD_TXT.format(
                                        protect_content = protect_content,
                                        hide_caption = hide_caption,
                                        channel_button = channel_button,
                                        name = name,
                                        link = link
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd)),
                )                   
            except Exception as e:
                print(f"! Error Occured on callback data = 'files_cmd' : {e}")
            
    elif data == "pc":
        if await authoUser(query, query.from_user.id) :
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....") 
                
            try:
                pic, protect_content, pcd = await fileSettings(ocean.get_protect_content, ocean.set_protect_content)
                hide_caption, hcd = await fileSettings(ocean.get_hide_caption)   
                channel_button, cbd = await fileSettings(ocean.get_channel_button) 
                name, link = await ocean.get_channel_button_link()
                
                await query.edit_message_media(
                    InputMediaPhoto(pic,
                                    FILES_CMD_TXT.format(
                                        protect_content = protect_content,
                                        hide_caption = hide_caption,
                                        channel_button = channel_button,
                                        name = name,
                                        link = link
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd))
                )                   
            except Exception as e:
                print(f"! Error Occured on callback data = 'pc' : {e}")
                
    elif data == "hc":
        if await authoUser(query, query.from_user.id) :
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....") 
                
            try:
                protect_content, pcd = await fileSettings(ocean.get_protect_content)
                pic, hide_caption, hcd = await fileSettings(ocean.get_hide_caption, ocean.set_hide_caption)   
                channel_button, cbd = await fileSettings(ocean.get_channel_button) 
                name, link = await ocean.get_channel_button_link()
                
                await query.edit_message_media(
                    InputMediaPhoto(pic,
                                    FILES_CMD_TXT.format(
                                        protect_content = protect_content,
                                        hide_caption = hide_caption,
                                        channel_button = channel_button,
                                        name = name,
                                        link = link
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd))
                )                   
            except Exception as e:
                print(f"! Error Occured on callback data = 'hc' : {e}")
            
    elif data == "cb":
        if await authoUser(query, query.from_user.id) :
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....") 
                
            try:
                protect_content, pcd = await fileSettings(ocean.get_protect_content)
                hide_caption, hcd = await fileSettings(ocean.get_hide_caption)   
                pic, channel_button, cbd = await fileSettings(ocean.get_channel_button, ocean.set_channel_button) 
                name, link = await ocean.get_channel_button_link()
                
                await query.edit_message_media(
                    InputMediaPhoto(pic,
                                    FILES_CMD_TXT.format(
                                        protect_content = protect_content,
                                        hide_caption = hide_caption,
                                        channel_button = channel_button,
                                        name = name,
                                        link = link
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup(buttonStatus(pcd, hcd, cbd))
                )                   
            except Exception as e:
                print(f"! Error Occured on callback data = 'cb' : {e}")
            
    elif data == "setcb":
        id = query.from_user.id
        if await authoUser(query, id) :
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....") 
                
            try:
                button_name, button_link = await ocean.get_channel_button_link()
            
                button_preview = [[InlineKeyboardButton(text=button_name, url=button_link)]]  
                set_msg = await client.ask(chat_id = id, text=f'<b>Tᴏ ᴄʜᴀɴɢᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴ, Pʟᴇᴀsᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛs ᴡɪᴛʜɪɴ 1 ᴍɪɴᴜᴛᴇ.\nFᴏʀ ᴇxᴀᴍᴘʟᴇ:\n<blockquote><code>Join Channel - https://t.me/btth480p</code></blockquote>\n\n<i>Bᴇʟᴏᴡ ɪs ʙᴜᴛᴛᴏɴ Pʀᴇᴠɪᴇᴡ ⬇️</i></b>', timeout=60, reply_markup=InlineKeyboardMarkup(button_preview), disable_web_page_preview = True)
                button = set_msg.text.split(' - ')
                
                if len(button) != 2:
                    markup = [[InlineKeyboardButton(f'◈ Sᴇᴛ Cʜᴀɴɴᴇʟ Bᴜᴛᴛᴏɴ ➪', callback_data='setcb')]]
                    return await set_msg.reply("<b>Pʟᴇᴀsᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛs.\nFᴏʀ ᴇxᴀᴍᴘʟᴇ:\n<blockquote><code>Join Channel - https://t.me/btth480p</code></blockquote>\n\n<i>Tʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ..</i></b>", reply_markup=InlineKeyboardMarkup(markup), disable_web_page_preview = True)
                
                button_name = button[0].strip(); button_link = button[1].strip()
                button_preview = [[InlineKeyboardButton(text=button_name, url=button_link)]]
                
                await set_msg.reply("<b><i>Aᴅᴅᴇᴅ Sᴜᴄcᴇssғᴜʟʟʏ ✅</i>\n<blockquote>Sᴇᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴀs Pʀᴇᴠɪᴇᴡ ⬇️</blockquote></b>", reply_markup=InlineKeyboardMarkup(button_preview))
                await ocean.set_channel_button_link(button_name, button_link)
                return
            except Exception as e:
                try:
                    await set_msg.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>")
                    print(f"! Error Occured on callback data = 'setcb' : {e}")
                except:
                    await client.send_message(id, text=f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote><i>Rᴇᴀsᴏɴ: 1 minute Time out ..</i></b></blockquote>", disable_notification=True)
                    print(f"! Error Occured on callback data = 'setcb' -> Rᴇᴀsᴏɴ: 1 minute Time out ..")

    elif data == 'autodel_cmd':
        if await authoUser(query, query.from_user.id, owner_only=True) :
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....") 
                
            try:
                timer = convert_time(await ocean.get_del_timer())
                autodel_mode, mode = await fileSettings(ocean.get_auto_delete, delfunc=True)
                
                await query.edit_message_media(
                    InputMediaPhoto(autodel_cmd_pic,
                                    AUTODEL_CMD_TXT.format(
                                        autodel_mode = autodel_mode,
                                        timer = timer
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup([
                        [InlineKeyboardButton(mode, callback_data='chng_autodel'), InlineKeyboardButton('◈ Sᴇᴛ Tɪᴍᴇʀ ⏱', callback_data='set_timer')],
                        [InlineKeyboardButton('🔄 Rᴇғʀᴇsʜ', callback_data='autodel_cmd'), InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')]
                    ])
                )
            except Exception as e:
                print(f"! Error Occured on callback data = 'autodel_cmd' : {e}")
            
    elif data == 'chng_autodel':
        if await authoUser(query, query.from_user.id, owner_only=True) :
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
                
            try:
                timer = convert_time(await ocean.get_del_timer())
                pic, autodel_mode, mode = await fileSettings(ocean.get_auto_delete, ocean.set_auto_delete, delfunc=True)
            
                await query.edit_message_media(
                    InputMediaPhoto(pic,
                                    AUTODEL_CMD_TXT.format(
                                        autodel_mode = autodel_mode,
                                        timer = timer
                                    )
                    ),
                    reply_markup = InlineKeyboardMarkup([
                        [InlineKeyboardButton(mode, callback_data='chng_autodel'), InlineKeyboardButton('◈ Sᴇᴛ Tɪᴍᴇʀ ⏱', callback_data='set_timer')],
                        [InlineKeyboardButton('🔄 Rᴇғʀᴇsʜ', callback_data='autodel_cmd'), InlineKeyboardButton('Cʟᴏsᴇ ✖️', callback_data='close')]
                    ])
                )
            except Exception as e:
                print(f"! Error Occured on callback data = 'chng_autodel' : {e}")

    elif data == 'set_timer':
        id = query.from_user.id
        if await authoUser(query, id, owner_only=True) :
            try:
                
                timer = convert_time(await ocean.get_del_timer())
                set_msg = await client.ask(chat_id=id, text=f'<b><blockquote>⏱ Cᴜʀʀᴇɴᴛ Tɪᴍᴇʀ: {timer}</blockquote>\n\nTᴏ ᴄʜᴀɴɢᴇ ᴛɪᴍᴇʀ, Pʟᴇᴀsᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ɪɴ sᴇᴄᴏɴᴅs ᴡɪᴛʜɪɴ 1 ᴍɪɴᴜᴛᴇ.\n<blockquote>Fᴏʀ ᴇxᴀᴍᴘʟᴇ: <code>300</code>, <code>600</code>, <code>900</code></b></blockquote>', timeout=60)
                del_timer = set_msg.text.split()
                
                if len(del_timer) == 1 and del_timer[0].isdigit():
                    DEL_TIMER = int(del_timer[0])
                    await ocean.set_del_timer(DEL_TIMER)
                    timer = convert_time(DEL_TIMER)
                    await set_msg.reply(f"<b><i>Aᴅᴅᴇᴅ Sᴜᴄcᴇssғᴜʟʟʏ ✅</i>\n<blockquote>⏱ Cᴜʀʀᴇɴᴛ Tɪᴍᴇʀ: {timer}</blockquote></b>")
                else:
                    markup = [[InlineKeyboardButton('◈ Sᴇᴛ Dᴇʟᴇᴛᴇ Tɪᴍᴇʀ ⏱', callback_data='set_timer')]]
                    return await set_msg.reply("<b>Pʟᴇᴀsᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ɪɴ sᴇᴄᴏɴᴅs.\n<blockquote>Fᴏʀ ᴇxᴀᴍᴘʟᴇ: <code>300</code>, <code>600</code>, <code>900</code></blockquote>\n\n<i>Tʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ..</i></b>", reply_markup=InlineKeyboardMarkup(markup))
    
            except Exception as e:
                try:
                    await set_msg.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>")
                    print(f"! Error Occured on callback data = 'set_timer' : {e}")
                except:
                    await client.send_message(id, text=f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ..\n<blockquote><i>Rᴇᴀsᴏɴ: 1 minute Time out ..</i></b></blockquote>", disable_notification=True)
                    print(f"! Error Occured on callback data = 'set_timer' -> Rᴇᴀsᴏɴ: 1 minute Time out ..")

    elif data == 'chng_req':
        if await authoUser(query, query.from_user.id, owner_only=True) :
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
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
                
                # Synchronize in-memory optimization
                client.REQFSUB = await ocean.get_request_forcesub()
        
                button = [
                    [InlineKeyboardButton(f"{on} ON", "chng_req"), InlineKeyboardButton(f"{off} OFF", "chng_req")],
                    [InlineKeyboardButton("⚙️ Mᴏʀᴇ Sᴇᴛᴛɪɴɢs ⚙️", "more_settings")]
                ]
                await query.message.edit_text(text=RFSUB_CMD_TXT.format(req_mode=texting), reply_markup=InlineKeyboardMarkup(button)) #🎉)
        
            except Exception as e:
                print(f"! Error Occured on callback data = 'chng_req' : {e}")


    elif data == 'more_settings':
        if await authoUser(query, query.from_user.id, owner_only=True) :
            #await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
            try:
                await query.message.edit_text("<b>Pʟᴇᴀsᴇ wᴀɪᴛ !\n\n<i>🔄 Rᴇᴛʀɪᴇᴠɪɴɢ ᴀʟʟ Sᴇᴛᴛɪɴɢs...</i></b>")
                LISTS = "Eᴍᴘᴛʏ Rᴇǫᴜᴇsᴛ FᴏʀᴄᴇSᴜʙ Cʜᴀɴɴᴇʟ Lɪsᴛ !?"
                
                REQFSUB_CHNLS = await ocean.get_reqChannel()
                if REQFSUB_CHNLS:
                    LISTS = ""
                    channel_name = "<i>Uɴᴀʙʟᴇ Lᴏᴀᴅ Nᴀᴍᴇ..</i>"
                    for CHNL in REQFSUB_CHNLS:
                        await query.message.reply_chat_action(ChatAction.TYPING)
                        try:
                            name = (await client.get_chat(CHNL)).title
                        except:
                            name = None
                        channel_name = name if name else channel_name
                        
                        user = await ocean.get_reqSent_user(CHNL)
                        channel_users = len(user) if user else 0
                        
                        link = await ocean.get_stored_reqLink(CHNL)
                        if link:
                            channel_name = f"<a href={link}>{channel_name}</a>"
    
                        LISTS += f"NAME: {channel_name}\n(ID: <code>{CHNL}</code>)\nUSERS: {channel_users}\n\n"
                        
                buttons = [
                    [InlineKeyboardButton("cʟᴇᴀʀ cʜᴀɴɴᴇʟs", "clear_chnls"), InlineKeyboardButton("cʟᴇᴀʀ ʟɪɴᴋs", "clear_links")],
                    [InlineKeyboardButton("♻️  Rᴇғʀᴇsʜ Sᴛᴀᴛᴜs  ♻️", "more_settings")],
                    [InlineKeyboardButton("⬅️ Bᴀᴄᴋ", "req_fsub"), InlineKeyboardButton("Cʟᴏsᴇ ✖️", "close")]
                ]
                await query.message.reply_chat_action(ChatAction.CANCEL)
                await query.message.edit_text(text=RFSUB_MS_TXT.format(reqfsub_list=LISTS.strip()), reply_markup=InlineKeyboardMarkup(buttons))
                        
            except Exception as e:
                print(f"! Error Occured on callback data = 'more_settings' : {e}")


    elif data == 'clear_users':
        #if await authoUser(query, query.from_user.id, owner_only=True) :
        #await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")    
        try:
            REQFSUB_CHNLS = await ocean.get_reqChannel()
            if not REQFSUB_CHNLS:
                return await query.answer("Eᴍᴘᴛʏ Rᴇǫᴜᴇsᴛ FᴏʀᴄᴇSᴜʙ Cʜᴀɴɴᴇʟ !?", show_alert=True)

            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
                
            REQFSUB_CHNLS = list(map(str, REQFSUB_CHNLS))    
            buttons = [REQFSUB_CHNLS[i:i+2] for i in range(0, len(REQFSUB_CHNLS), 2)]
            buttons.insert(0, ['CANCEL'])
            buttons.append(['DELETE ALL CHANNELS USER'])

            user_reply = await client.ask(query.from_user.id, text=CLEAR_USERS_TXT, reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
            
            if user_reply.text == 'CANCEL':
                return await user_reply.reply("<b><i>🆑 Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>", reply_markup=ReplyKeyboardRemove())
                
            elif user_reply.text in REQFSUB_CHNLS:
                try:
                    await ocean.clear_reqSent_user(int(user_reply.text))
                    return await user_reply.reply(f"<b><blockquote>✅ Usᴇʀ Dᴀᴛᴀ Sᴜᴄᴄᴇssғᴜʟʟʏ Cʟᴇᴀʀᴇᴅ ғʀᴏᴍ Cʜᴀɴɴᴇʟ ɪᴅ: <code>{user_reply.text}</code></blockquote></b>", reply_markup=ReplyKeyboardRemove())
                except Exception as e:
                    return await user_reply.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>", reply_markup=ReplyKeyboardRemove())
                    
            elif user_reply.text == 'DELETE ALL CHANNELS USER':
                try:
                    for CHNL in REQFSUB_CHNLS:
                        await ocean.clear_reqSent_user(int(CHNL))
                    return await user_reply.reply(f"<b><blockquote>✅ Usᴇʀ Dᴀᴛᴀ Sᴜᴄᴄᴇssғᴜʟʟʏ Cʟᴇᴀʀᴇᴅ ғʀᴏᴍ Aʟʟ Cʜᴀɴɴᴇʟ ɪᴅs</blockquote></b>", reply_markup=ReplyKeyboardRemove())
                except Exception as e:
                    return await user_reply.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>", reply_markup=ReplyKeyboardRemove())
                    
            else:
                return await user_reply.reply(f"<b><blockquote>INVALID SELECTIONS</blockquote></b>", reply_markup=ReplyKeyboardRemove())
            
        except Exception as e:
            print(f"! Error Occured on callback data = 'clear_users' : {e}")


    elif data == 'clear_chnls':
        #if await authoUser(query, query.from_user.id, owner_only=True) 
            
        try:
            REQFSUB_CHNLS = await ocean.get_reqChannel()
            if not REQFSUB_CHNLS:
                return await query.answer("Eᴍᴘᴛʏ Rᴇǫᴜᴇsᴛ FᴏʀᴄᴇSᴜʙ Cʜᴀɴɴᴇʟ !?", show_alert=True)
            
            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
                
            REQFSUB_CHNLS = list(map(str, REQFSUB_CHNLS))    
            buttons = [REQFSUB_CHNLS[i:i+2] for i in range(0, len(REQFSUB_CHNLS), 2)]
            buttons.insert(0, ['CANCEL'])
            buttons.append(['DELETE ALL CHANNEL IDS'])

            user_reply = await client.ask(query.from_user.id, text=CLEAR_CHNLS_TXT, reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
            
            if user_reply.text == 'CANCEL':
                return await user_reply.reply("<b><i>🆑 Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>", reply_markup=ReplyKeyboardRemove())
                
            elif user_reply.text in REQFSUB_CHNLS:
                try:
                    await ocean.del_reqChannel(int(user_reply.text))
                    
                    # Synchronize in-memory optimization
                    client.CHANNEL_LIST = await ocean.get_all_channels()
                    
                    return await user_reply.reply(f"<b><blockquote><code>{user_reply.text}</code> Cʜᴀɴɴᴇʟ Iᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ ✅</blockquote></b>", reply_markup=ReplyKeyboardRemove())
                except Exception as e:
                    return await user_reply.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>", reply_markup=ReplyKeyboardRemove())
                    
            elif user_reply.text == 'DELETE ALL CHANNEL IDS':
                try:
                    for CHNL in REQFSUB_CHNLS:
                        await ocean.del_reqChannel(int(CHNL))
                    
                    # Synchronize in-memory optimization
                    client.CHANNEL_LIST = await ocean.get_all_channels()
                    
                    return await user_reply.reply(f"<b><blockquote>Aʟʟ Cʜᴀɴɴᴇʟ Iᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ ✅</blockquote></b>", reply_markup=ReplyKeyboardRemove())
                except Exception as e:
                    return await user_reply.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>", reply_markup=ReplyKeyboardRemove())
                    
            else:
                return await user_reply.reply(f"<b><blockquote>INVALID SELECTIONS</blockquote></b>", reply_markup=ReplyKeyboardRemove())
            
        except Exception as e:
            print(f"! Error Occured on callback data = 'more_settings' : {e}")



    elif data == 'clear_links':
        #if await authoUser(query, query.from_user.id, owner_only=True) :
        #await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
            
        try:
            REQFSUB_CHNLS = await ocean.get_reqLink_channels()
            if not REQFSUB_CHNLS:
                return await query.answer("Nᴏ Sᴛᴏʀᴇᴅ Rᴇǫᴜᴇsᴛ Lɪɴᴋ Aᴠᴀɪʟᴀʙʟᴇ !?", show_alert=True)

            await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
                
            REQFSUB_CHNLS = list(map(str, REQFSUB_CHNLS))    
            buttons = [REQFSUB_CHNLS[i:i+2] for i in range(0, len(REQFSUB_CHNLS), 2)]
            buttons.insert(0, ['CANCEL'])
            buttons.append(['DELETE ALL REQUEST LINKS'])

            user_reply = await client.ask(query.from_user.id, text=CLEAR_LINKS_TXT, reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
            
            if user_reply.text == 'CANCEL':
                return await user_reply.reply("<b><i>🆑 Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>", reply_markup=ReplyKeyboardRemove())
                
            elif user_reply.text in REQFSUB_CHNLS:
                channel_id = int(user_reply.text)
                try:
                    try:
                        await client.revoke_chat_invite_link(channel_id, await ocean.get_stored_reqLink(channel_id))
                    except:
                        text = """<b>❌ Uɴᴀʙʟᴇ ᴛᴏ Rᴇᴠᴏᴋᴇ ʟɪɴᴋ !
<blockquote expandable>ɪᴅ: <code>{}</code></b>
<i>Eɪᴛʜᴇʀ ᴛʜᴇ ʙᴏᴛ ɪs ɴᴏᴛ ɪɴ ᴀʙᴏᴠᴇ ᴄʜᴀɴɴᴇʟ Oʀ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘʀᴏᴘᴇʀ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs</i></blockquote>"""
                        return await user_reply.reply(text=text.format(channel_id), reply_markup=ReplyKeyboardRemove())
                        
                    await ocean.del_stored_reqLink(channel_id)
                    return await user_reply.reply(f"<b><blockquote><code>{channel_id}</code> Cʜᴀɴɴᴇʟs Lɪɴᴋ Sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ ✅</blockquote></b>", reply_markup=ReplyKeyboardRemove())
                
                except Exception as e:
                    return await user_reply.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>", reply_markup=ReplyKeyboardRemove())
                    
            elif user_reply.text == 'DELETE ALL REQUEST LINKS':
                try:
                    result = ""
                    for CHNL in REQFSUB_CHNLS:
                        channel_id = int(CHNL)
                        try:
                            await client.revoke_chat_invite_link(channel_id, await ocean.get_stored_reqLink(channel_id))
                        except:
                            result += f"<blockquote expandable><b><code>{channel_id}</code> Uɴᴀʙʟᴇ ᴛᴏ Rᴇᴠᴏᴋᴇ ❌</b>\n<i>Eɪᴛʜᴇʀ ᴛʜᴇ ʙᴏᴛ ɪs ɴᴏᴛ ɪɴ ᴀʙᴏᴠᴇ ᴄʜᴀɴɴᴇʟ Oʀ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘʀᴏᴘᴇʀ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs.</i></blockquote>\n"
                            continue
                        await ocean.del_stored_reqLink(channel_id)
                        result += f"<blockquote><b><code>{channel_id}</code> IDs Lɪɴᴋ Dᴇʟᴇᴛᴇᴅ ✅</b></blockquote>\n"
                        
                    return await user_reply.reply(f"<b>⁉️ Oᴘᴇʀᴀᴛɪᴏɴ Rᴇsᴜʟᴛ:</b>\n{result.strip()}", reply_markup=ReplyKeyboardRemove())
 
                except Exception as e:
                    return await user_reply.reply(f"<b>! Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ...\n<blockquote>Rᴇᴀsᴏɴ:</b> {e}</blockquote>", reply_markup=ReplyKeyboardRemove())
                    
            else:
                return await user_reply.reply(f"<b><blockquote>INVALID SELECTIONS</blockquote></b>", reply_markup=ReplyKeyboardRemove())
            
        except Exception as e:
            print(f"! Error Occured on callback data = 'more_settings' : {e}")
            

    elif data == 'req_fsub':
        #if await authoUser(query, query.from_user.id, owner_only=True) :
        await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....")
    
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
                [InlineKeyboardButton("⚙️ Mᴏʀᴇ Sᴇᴛᴛɪɴɢs ⚙️", "more_settings")]
            ]
            await query.message.edit_text(text=RFSUB_CMD_TXT.format(req_mode=texting), reply_markup=InlineKeyboardMarkup(button)) #🎉)
    
        except Exception as e:
            print(f"! Error Occured on callback data = 'chng_req' : {e}")

    elif data == 'flink:status':
        user_id = query.from_user.id

        await query.message.edit_text("<b><i>🔄 Rᴇғʀᴇsʜɪɴɢ....</i></b>")
        await format_status_msg(query.message, user_id)


    elif data == 'flink:change_format':
        user_id = query.from_user.id

        temp = await query.message.reply(
            f'<b>Sᴇɴᴅ ʟɪɴᴋ ғᴏʀᴍᴀᴛ: Qᴜᴀʟɪᴛʏ ᴡɪᴛʜ ʀᴇsᴘᴇᴄᴛɪᴠᴇ ᴛᴏ ᴍᴇssᴀɢᴇ ʟᴇɴɢᴛʜ\n\n{EXAMPLES}</b>',
            reply_markup=cancelKeyboard
        )

        rcv_msg = await client.listen(chat_id=user_id)
        await del_msg(temp)

        TEXT = rcv_msg.text

        if TEXT is None:
            return await rcv_msg.reply("<b>⚠️ Pʟᴇᴀsᴇ, ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɪɴᴘᴜᴛ (ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴏɴʟʏ)</b>", reply_markup=closeButton, quote=True)

        if TEXT == 'CANCEL':
            return await rcv_msg.reply(f"<b><i>🆑 Oᴘᴇʀᴀᴛɪᴏɴ Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>", reply_markup=closeButton, quote=True)
        
        format_lines = TEXT.splitlines()

        try:
            for line in format_lines:
                msg_txt_and_lengths = line.split(',')

                for msg_data in msg_txt_and_lengths:
                    msg_txt, msg_len = msg_data.strip().split(' = ')
                    msg_len = int(msg_len)

        except Exception as e:
            print(f"---- Invalide format received ----\nFormat: {TEXT}\n\nReason: {e}\n-----------------------")
            return await rcv_msg.reply(
                f"<b>⚠️ Iɴᴠᴀʟɪᴅ Fᴏʀᴍᴀᴛ, ғᴏʟʟᴏᴡ ʙᴇʟᴏᴡ\n\n{EXAMPLES}</b>", 
                reply_markup=closeButton,
                quote=True
            )
        
        else:
            format_data[user_id] = TEXT
            return await rcv_msg.reply(
                f"<b><i>Lɪɴᴋ Fᴏʀᴍᴀᴛ ᴀᴅᴅᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ ✅</i></b>", 
                reply_markup=closeButton,
                quote=True
            )
            

    elif data == 'flink:start':
        user_id = query.from_user.id

        link_formats = format_data.get(user_id)
        if not link_formats:
            return await query.answer('⚠️ Fɪʀsᴛ sᴇᴛ ᴛʜᴇ ʟɪɴᴋ ғᴏʀᴍᴀᴛ', show_alert=True)
        
        link = client.db_channel.invite_link
        channel = f"<a href={link}>ᴅʙ ᴄʜᴀɴɴᴇʟ</a>" if link else 'ᴅʙ ᴄʜᴀɴɴᴇʟ'

        while True:
            try:
                tmp = await query.message.reply(
                    text=f"<b><blockquote>Fᴏʀᴡᴀʀᴅ ᴛʜᴇ Mᴇssᴀɢᴇ ғʀᴏᴍ {channel} (ᴡɪᴛʜ ǫᴜᴏᴛᴇs)..</blockquote>\n<blockquote>Oʀ Sᴇɴᴅ ᴛʜᴇ {channel} Pᴏsᴛ Lɪɴᴋ</blockquote></b>",
                    reply_markup=cancelKeyboard,
                    disable_web_page_preview=True
                )

                channel_message = await client.listen(chat_id=user_id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)))

                if channel_message.text == 'CANCEL':
                    return await del_msg(channel_message, tmp)

            except:
                try: return await del_msg(tmp)
                except: return
            
            msg_id = await GET_MESSAGE_ID(client, channel_message)

            if msg_id:
                await del_msg(tmp)
                break
            else:
                await del_msg(tmp)
                
                await channel_message.reply(
                    f"<b>❌ Eʀʀᴏʀ..\n<blockquote>Tʜɪs Fᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏsᴛ ᴏʀ ᴍᴇssᴀɢᴇ ʟɪɴᴋ ɪs ɴᴏᴛ ғʀᴏᴍ ᴍʏ {channel}</blockquote></b>", 
                    quote=True, 
                    reply_markup=closeButton,
                    disable_web_page_preview=True
                )
                continue

        format_lines = link_formats.splitlines()

        output_txt = []

        for line in format_lines:
            msg_txt_and_lengths = line.split(',')
            qlty_links = []

            for msg_data in msg_txt_and_lengths:
                msg_txt, msg_len = msg_data.strip().split(' = ')
                msg_len = int(msg_len)

                if msg_len == 1:
                    msg = f'get-{msg_id * abs(client.db_channel.id)}'
                    msg_id += 1
                
                else:
                    first_msg = f'{msg_id * abs(client.db_channel.id)}'
                    msg_id += (msg_len-1)

                    last_msg = f'{msg_id * abs(client.db_channel.id)}'
                    msg_id += 1

                    msg = f'get-{first_msg}-{last_msg}'
                
                encoded_msg = await ENCODE_MSG(msg)
                msg_link = f"https://t.me/{client.username}?start={encoded_msg}"

                qlty_links.append(f'{msg_txt} - {msg_link}')

            output_txt.append(" | ".join(qlty_links))

        final_message = '\n'.join(output_txt)
        
        inline_buttons = make_inline_button(final_message)
        await channel_message.reply(text=f'<b>⬇️ Bᴇʟᴏᴡ ɪs ᴛʜᴇ ғᴏʀᴍᴀᴛᴇᴅ ʟɪɴᴋ::</b>\n\n<blockquote><code>{final_message}</code></blockquote>', reply_markup=inline_buttons, quote=True, disable_web_page_preview=True)     

        
            
                
                    
                 
