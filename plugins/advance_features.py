import re
from bot import Bot
import asyncio
from pyrogram.enums import ParseMode, ChatAction
from helper_func import is_admin, banUser
from plugins.FORMATS import *
from plugins.autoDelete import convert_time
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNER_ID
from helper_func import S, stylish_text
from pyrogram import Client, filters
from database.database import ocean

# ── Force-Sub channel management ─────────────────────────────────────────────

@Bot.on_message(filters.command('add_fsub') & filters.private & filters.user(OWNER_ID))
async def add_forcesub(client: Client, message: Message):
    pro = await message.reply(S("<b><i>Processing...</i></b>"), quote=True)
    check = 0
    channel_ids = await ocean.get_all_channels()
    fsubs = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])

    if not fsubs:
        await pro.edit(
            S("<b>No channel IDs provided.\n<blockquote><u>USAGE</u>:\n/add_fsub [channel_ids] :</b> add one or multiple channel IDs at once.</blockquote>"),
            reply_markup=reply_markup
        )
        return

    channel_list = ""
    for id in fsubs:
        try:
            id = int(id)
        except Exception:
            channel_list += S(f"<b><blockquote>Invalid ID: <code>{id}</code></blockquote></b>\n\n")
            continue

        if id in channel_ids:
            channel_list += S(f"<blockquote><b>ID: <code>{id}</code>, already registered.</b></blockquote>\n\n")
            continue

        id = str(id)
        if id.startswith('-') and id[1:].isdigit() and len(id) == 14:
            try:
                link = (await client.get_chat(id)).invite_link
                cname = (await client.get_chat(id)).title
                if not link:
                    await client.export_chat_invite_link(id)
                    link = (await client.get_chat(id)).invite_link
                channel_list += S(f"<b><blockquote>Name: <a href={link}>{cname}</a> (ID: <code>{id}</code>)</blockquote></b>\n\n")
                check += 1
            except Exception:
                channel_list += S(f"<b><blockquote>ID: <code>{id}</code>\n<i>Could not add force-sub — verify the channel ID and bot permissions.</i></blockquote></b>\n\n")
        else:
            channel_list += S(f"<b><blockquote>Invalid ID: <code>{id}</code></blockquote></b>\n\n")
            continue

    if check == len(fsubs):
        for id in fsubs:
            await ocean.add_channel(int(id))
        client.CHANNEL_LIST = await ocean.get_all_channels()
        await pro.edit(
            S(f'<b>Force-Sub channel added successfully ✅</b>\n\n{channel_list}'),
            reply_markup=reply_markup, disable_web_page_preview=True
        )
    else:
        await pro.edit(
            S(f'<b>⚠️ Some channels could not be added.</b>\n\n{channel_list.strip()}\n\n<b><i>Please try again.</i></b>'),
            reply_markup=reply_markup, disable_web_page_preview=True
        )


@Bot.on_message(filters.command('del_fsub') & filters.private & filters.user(OWNER_ID))
async def delete_all_forcesub(client: Client, message: Message):
    pro = await message.reply(S("<b><i>Processing...</i></b>"), quote=True)
    channels = await ocean.get_all_channels()
    fsubs = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])

    if not fsubs:
        return await pro.edit(
            S("<b>⁉️ Please provide valid IDs or arguments.\n<blockquote><u>USAGE</u>:\n/del_fsub [channel_ids] :</b> remove one or more specific IDs\n<code>/del_fsub all</code> : remove every force-sub ID</blockquote>"),
            reply_markup=reply_markup
        )

    if len(fsubs) == 1 and fsubs[0].lower() == "all":
        if channels:
            for id in channels:
                await ocean.del_channel(id)
            client.CHANNEL_LIST = await ocean.get_all_channels()
            ids = "\n".join(f"<blockquote><code>{ch}</code> ✅</blockquote>" for ch in channels)
            return await pro.edit(S(f"<b>🗑 All force-sub channel IDs removed:\n{ids}</b>"), reply_markup=reply_markup)
        else:
            return await pro.edit(S("<b><blockquote>⁉️ No channel IDs found to remove.</blockquote></b>"), reply_markup=reply_markup)

    if len(channels) >= 1:
        passed = ''
        for sub_id in fsubs:
            try:
                id = int(sub_id)
            except Exception:
                passed += S(f"<b><blockquote><i>Invalid ID: <code>{sub_id}</code></i></blockquote></b>\n")
                continue
            if id in channels:
                await ocean.del_channel(id)
                passed += f"<blockquote><code>{id}</code> ✅</blockquote>\n"
            else:
                passed += S(f"<b><blockquote><code>{id}</code> not found in force-sub list.</blockquote></b>\n")
        client.CHANNEL_LIST = await ocean.get_all_channels()
        await pro.edit(S(f"<b>🗑 Specified channel IDs removed:\n\n{passed}</b>"), reply_markup=reply_markup)
    else:
        await pro.edit(S("<b><blockquote>⁉️ No channel IDs available to remove.</blockquote></b>"), reply_markup=reply_markup)


@Bot.on_message(filters.command('fsub_chnl') & filters.private & is_admin)
async def get_forcesub(client: Client, message: Message):
    pro = await message.reply(S("<b><i>Processing...</i></b>"), quote=True)
    channels = await ocean.get_all_channels()
    channel_list = S("<b><blockquote>❌ No force-sub channels found.</b></blockquote>")

    if channels:
        channel_list = ""
        for id in channels:
            await message.reply_chat_action(ChatAction.TYPING)
            try:
                link = (await client.get_chat(id)).invite_link
                cname = (await client.get_chat(id)).title
                if not link:
                    await client.export_chat_invite_link(id)
                    link = (await client.get_chat(id)).invite_link
                channel_list += S(f"<b><blockquote>Name: <a href={link}>{cname}</a>\n(ID: <code>{id}</code>)</blockquote></b>\n\n")
            except Exception:
                channel_list += S(f"<b><blockquote>ID: <code>{id}</code>\n<i>Could not load details.</i></blockquote></b>\n\n")

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])
    await message.reply_chat_action(ChatAction.CANCEL)
    await pro.edit(
        S(f"<b>📋 FORCE-SUB CHANNEL LIST:</b>\n\n{channel_list}"),
        reply_markup=reply_markup, disable_web_page_preview=True
    )


@Bot.on_message(filters.command('add_admins') & filters.private & filters.user(OWNER_ID))
async def add_admins(client: Client, message: Message):
    pro = await message.reply(S("<b><i>Processing...</i></b>"), quote=True)
    check = 0
    admin_ids = await ocean.get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])

    if not admins:
        return await pro.edit(
            S("<b>No user IDs provided.\n<blockquote><u>USAGE</u>:\n/add_admins [user_id] :</b> add one or multiple user IDs at once.</blockquote>"),
            reply_markup=reply_markup
        )

    admin_list = ""
    for id in admins:
        try:
            id = int(id)
        except Exception:
            admin_list += S(f"<blockquote><b>Invalid ID: <code>{id}</code></b></blockquote>\n")
            continue

        if id in admin_ids:
            admin_list += S(f"<blockquote><b>ID: <code>{id}</code>, already registered.</b></blockquote>\n")
            continue

        id = str(id)
        if id.isdigit() and len(id) == 10:
            admin_list += f"<b><blockquote>(ID: <code>{id}</code>)</blockquote></b>\n"
            check += 1
        else:
            admin_list += S(f"<blockquote><b>Invalid ID: <code>{id}</code></b></blockquote>\n")
            continue

    if check == len(admins):
        for id in admins:
            await ocean.add_admin(int(id))
        await pro.edit(S(f'<b>New IDs added to admin list ✅</b>\n\n{admin_list}'), reply_markup=reply_markup)
    else:
        await pro.edit(S(f'<b>⚠️ Some IDs could not be added.</b>\n\n{admin_list.strip()}\n\n<b><i>Please try again.</i></b>'), reply_markup=reply_markup)


@Bot.on_message(filters.command('del_admins') & filters.private & filters.user(OWNER_ID))
async def delete_admins(client: Client, message: Message):
    pro = await message.reply(S("<b><i>Processing...</i></b>"), quote=True)
    admin_ids = await ocean.get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])

    if not admins:
        return await pro.edit(
            S("<b>⁉️ Please provide valid IDs or arguments.</b>\n<blockquote><b><u>USAGE:</u>\n/del_admins [user_ids] :</b> remove one or more specific IDs\n<code>/del_admins all</code> : remove all admin IDs</blockquote>"),
            reply_markup=reply_markup
        )

    if len(admins) == 1 and admins[0].lower() == "all":
        if admin_ids:
            for id in admin_ids:
                await ocean.del_admin(id)
            ids = "\n".join(f"<blockquote><code>{a}</code> ✅</blockquote>" for a in admin_ids)
            return await pro.edit(S(f"<b>🗑 All admin IDs removed:\n{ids}</b>"), reply_markup=reply_markup)
        else:
            return await pro.edit(S("<b><blockquote>⁉️ No admin IDs available to remove.</blockquote></b>"), reply_markup=reply_markup)

    if len(admin_ids) >= 1:
        passed = ''
        for ad_id in admins:
            try:
                id = int(ad_id)
            except Exception:
                passed += S(f"<blockquote><b>Invalid ID: <code>{ad_id}</code></b></blockquote>\n")
                continue
            if id in admin_ids:
                await ocean.del_admin(id)
                passed += f"<blockquote><code>{id}</code> ✅</blockquote>\n"
            else:
                passed += S(f"<blockquote><b><code>{id}</code> not in admin list.</b></blockquote>\n")
        await pro.edit(S(f"<b>🗑 Specified admin IDs removed:\n\n{passed}</b>"), reply_markup=reply_markup)
    else:
        await pro.edit(S("<b><blockquote>⁉️ No admin IDs available to remove.</blockquote></b>"), reply_markup=reply_markup)


@Bot.on_message(filters.command('admin_list') & filters.private & filters.user(OWNER_ID))
async def get_admin_list(client: Client, message: Message):
    pro = await message.reply(S("<b><i>Processing...</i></b>"), quote=True)
    admin_ids = await ocean.get_all_admins()
    admin_list = S("<b><blockquote>❌ No admins registered yet.</blockquote></b>")

    if admin_ids:
        admin_list = ""
        for id in admin_ids:
            await message.reply_chat_action(ChatAction.TYPING)
            try:
                user = await client.get_users(id)
                user_link = f"tg://openmessage?user_id={id}"
                first_name = user.first_name if user.first_name else "No name"
                admin_list += S(f"<b><blockquote>Name: <a href={user_link}>{first_name}</a>\n(ID: <code>{id}</code>)</blockquote></b>\n\n")
            except Exception:
                admin_list += S(f"<b><blockquote>ID: <code>{id}</code>\n<i>Could not load details.</i></blockquote></b>\n\n")

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])
    await message.reply_chat_action(ChatAction.CANCEL)
    await pro.edit(
        S(f"<b>🤖 BOT ADMIN LIST:</b>\n\n{admin_list}"),
        reply_markup=reply_markup, disable_web_page_preview=True
    )

@Bot.on_message(filters.command('add_banuser') & filters.private & is_admin)
async def add_banuser(client: Client, message: Message):
    pro = await message.reply(S("<b><i>Processing...</i></b>"), quote=True)
    check, autho_users = 0, []
    banuser_ids = await ocean.get_ban_users()
    autho_users = await ocean.get_all_admins()
    autho_users.append(OWNER_ID)
    banusers = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])

    if not banusers:
        return await pro.edit(
            S("<b>No user IDs provided.\n<blockquote><u>USAGE</u>:\n/add_banuser [user_id] :</b> add one or multiple user IDs at once.</blockquote>"),
            reply_markup=reply_markup
        )

    banuser_list = ""
    for id in banusers:
        try:
            id = int(id)
        except Exception:
            banuser_list += S(f"<blockquote><b>Invalid ID: <code>{id}</code></b></blockquote>\n")
            continue

        if id in autho_users:
            banuser_list += S(f"<blockquote><b>ID: <code>{id}</code>, belongs to an admin or owner.</b></blockquote>\n")
            continue

        if id in banuser_ids:
            banuser_list += S(f"<blockquote><b>ID: <code>{id}</code>, already banned.</b></blockquote>\n")
            continue

        id = str(id)
        if id.isdigit() and len(id) == 10:
            banuser_list += f"<b><blockquote>(ID: <code>{id}</code>)</blockquote></b>\n"
            check += 1
        else:
            banuser_list += S(f"<blockquote><b>Invalid ID: <code>{id}</code></b></blockquote>\n")
            continue

    if check == len(banusers):
        for id in banusers:
            await ocean.add_ban_user(int(id))
        await pro.edit(S(f'<b>New IDs added to banned list ✅</b>\n\n{banuser_list}'), reply_markup=reply_markup)
    else:
        await pro.edit(S(f'<b>⚠️ Some IDs could not be banned.</b>\n\n{banuser_list.strip()}\n\n<b><i>Please try again.</i></b>'), reply_markup=reply_markup)


@Bot.on_message(filters.command('del_banuser') & filters.private & is_admin)
async def delete_banuser(client: Client, message: Message):
    pro = await message.reply(S("<b><i>Processing...</i></b>"), quote=True)
    banuser_ids = await ocean.get_ban_users()
    banusers = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])

    if not banusers:
        return await pro.edit(
            S("<b>⁉️ Please provide valid IDs or arguments.</b>\n<blockquote><b><u>USAGE:</u>\n/del_banuser [user_ids] :</b> remove one or more specific IDs\n<code>/del_banuser all</code> : remove all banned IDs</blockquote>"),
            reply_markup=reply_markup
        )

    if len(banusers) == 1 and banusers[0].lower() == "all":
        if banuser_ids:
            for id in banuser_ids:
                await ocean.del_ban_user(id)
            ids = "\n".join(f"<blockquote><code>{u}</code> ✅</blockquote>" for u in banuser_ids)
            return await pro.edit(S(f"<b>🗑 All banned user IDs removed:\n{ids}</b>"), reply_markup=reply_markup)
        else:
            return await pro.edit(S("<b><blockquote>⁉️ No banned user IDs available to remove.</blockquote></b>"), reply_markup=reply_markup)

    if len(banuser_ids) >= 1:
        passed = ''
        for ban_id in banusers:
            try:
                id = int(ban_id)
            except Exception:
                passed += S(f"<blockquote><b>Invalid ID: <code>{ban_id}</code></b></blockquote>\n")
                continue
            if id in banuser_ids:
                await ocean.del_ban_user(id)
                passed += f"<blockquote><code>{id}</code> ✅</blockquote>\n"
            else:
                passed += S(f"<blockquote><b><code>{id}</code> not in banned list.</b></blockquote>\n")
        await pro.edit(S(f"<b>🗑 Specified banned user IDs removed:\n\n{passed}</b>"), reply_markup=reply_markup)
    else:
        await pro.edit(S("<b><blockquote>⁉️ No banned user IDs available to remove.</blockquote></b>"), reply_markup=reply_markup)


@Bot.on_message(filters.command('banuser_list') & filters.private & is_admin)
async def get_banuser_list(client: Client, message: Message):
    pro = await message.reply(S("<b><i>Processing...</i></b>"), quote=True)
    banuser_ids = await ocean.get_ban_users()
    banuser_list = S("<b><blockquote>❌ No banned users found.</blockquote></b>")

    if banuser_ids:
        banuser_list = ""
        for id in banuser_ids:
            await message.reply_chat_action(ChatAction.TYPING)
            try:
                user = await client.get_users(id)
                user_link = f"tg://openmessage?user_id={id}"
                first_name = user.first_name if user.first_name else "No name"
                banuser_list += S(f"<b><blockquote>Name: <a href={user_link}>{first_name}</a>\n(ID: <code>{id}</code>)</blockquote></b>\n\n")
            except Exception:
                banuser_list += S(f"<b><blockquote>ID: <code>{id}</code>\n<i>Could not load details.</i></blockquote></b>\n\n")

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])
    await message.reply_chat_action(ChatAction.CANCEL)
    await pro.edit(
        S(f"<b>🚫 BANNED USER LIST:</b>\n\n{banuser_list}"),
        reply_markup=reply_markup, disable_web_page_preview=True
    )


# ── Auto-delete settings ──────────────────────────────────────────────────────

@Bot.on_message(filters.command('auto_del') & filters.private & ~banUser)
async def autoDelete_settings(client, message):
    await message.reply_chat_action(ChatAction.TYPING)
    try:
        timer = convert_time(await ocean.get_del_timer())
        if await ocean.get_auto_delete():
            autodel_mode = on_txt
            mode = S('Disable ❌')
        else:
            autodel_mode = off_txt
            mode = S('Enable ✅')

        await message.reply_photo(
            photo=autodel_cmd_pic,
            caption=AUTODEL_CMD_TXT.format(autodel_mode=autodel_mode, timer=timer),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(mode, callback_data='chng_autodel'), InlineKeyboardButton(S('⏱ Set Timer'), callback_data='set_timer')],
                [InlineKeyboardButton(S('🔄 Refresh'), callback_data='autodel_cmd'), InlineKeyboardButton(S('Close ✖️'), callback_data='close')]
            ]),
            message_effect_id=5107584321108051014
        )
    except Exception as e:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])
        await message.reply(
            S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote><b><i>Contact the developer: @OceanXBotz</i></b>"),
            reply_markup=reply_markup
        )


# ── File settings ─────────────────────────────────────────────────────────────

@Bot.on_message(filters.command('files') & filters.private & ~banUser)
async def files_commands(client: Client, message: Message):
    await message.reply_chat_action(ChatAction.TYPING)
    try:
        protect_content = hide_caption = channel_button = off_txt
        pcd = hcd = cbd = '❌'
        if await ocean.get_protect_content():
            protect_content = on_txt
            pcd = '✅'
        if await ocean.get_hide_caption():
            hide_caption = on_txt
            hcd = '✅'
        if await ocean.get_channel_button():
            channel_button = on_txt
            cbd = '✅'
        name, link = await ocean.get_channel_button_link()

        await message.reply_photo(
            photo=files_cmd_pic,
            caption=FILES_CMD_TXT.format(
                protect_content=protect_content,
                hide_caption=hide_caption,
                channel_button=channel_button,
                name=name,
                link=link
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(S(f'Protect Content: {pcd}'), callback_data='pc'), InlineKeyboardButton(S(f'Hide Caption: {hcd}'), callback_data='hc')],
                [InlineKeyboardButton(S(f'Channel Button: {cbd}'), callback_data='cb'), InlineKeyboardButton(S(f'Set Button ➪'), callback_data='setcb')],
                [InlineKeyboardButton(S('🔄 Refresh'), callback_data='files_cmd'), InlineKeyboardButton(S('Close ✖️'), callback_data='close')]
            ]),
            message_effect_id=5107584321108051014
        )
    except Exception as e:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])
        await message.reply(
            S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote><b><i>Contact the developer: @OceanXBotz</i></b>"),
            reply_markup=reply_markup
        )


# ── Request force-sub ─────────────────────────────────────────────────────────

@Bot.on_message(filters.command('req_fsub') & filters.private & ~banUser)
async def handle_reqFsub(client: Client, message: Message):
    await message.reply_chat_action(ChatAction.TYPING)
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
        await message.reply(
            text=RFSUB_CMD_TXT.format(req_mode=texting),
            reply_markup=InlineKeyboardMarkup(button),
            message_effect_id=5046509860389126442
        )
    except Exception as e:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(S("Close ✖️"), callback_data="close")]])
        await message.reply(
            S(f"<b>Something went wrong.\n<blockquote>Reason:</b> {e}</blockquote><b><i>Contact the developer: @OceanXBotz</i></b>"),
            reply_markup=reply_markup
        )