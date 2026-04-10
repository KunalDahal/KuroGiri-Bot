from bot import Bot
from database.database import ocean
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated

@Bot.on_chat_member_updated()
async def handle_Chatmembers(client, chat_member_updated: ChatMemberUpdated):
    chat_id = chat_member_updated.chat.id

    if await ocean.reqChannel_exist(chat_id):
        old_member = chat_member_updated.old_chat_member

        if not old_member:
            return

        if old_member.status == ChatMemberStatus.MEMBER:
            user_id = old_member.user.id

            if await ocean.reqSent_user_exist(chat_id, user_id):
                await ocean.del_reqSent_user(chat_id, user_id)


@Bot.on_chat_join_request()
async def handle_join_request(client, chat_join_request):
    chat_id = chat_join_request.chat.id

    if await ocean.reqChannel_exist(chat_id):
        user_id = chat_join_request.from_user.id

        if not await ocean.reqSent_user_exist(chat_id, user_id):
            await ocean.reqSent_user(chat_id, user_id)