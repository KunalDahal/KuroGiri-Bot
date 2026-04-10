import motor.motor_asyncio
import certifi
from config import DB_URI, DB_NAME

class SidDataBase:

    def __init__(self, DB_URI, DB_NAME):
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(
            DB_URI,
            tls=True,
            tlsCAFile=certifi.where()
        )
        self.db = self.dbclient[DB_NAME]
        self.database = self.dbclient[DB_NAME]
        
        self.user_data = self.database['users']
        self.channel_data = self.database['channels']
        self.admins_data = self.database['admins']
        self.banned_user_data = self.database['banned_user']
        self.autho_user_data = self.database['autho_user']
        
        self.auto_delete_data = self.database['auto_delete']
        self.hide_caption_data = self.database['hide_caption']
        self.protect_content_data = self.database['protect_content']
        self.channel_button_data = self.database['channel_button']
        
        self.del_timer_data = self.database['del_timer']
        self.channel_button_link_data = self.database['channelButton_link']

        self.rqst_fsub_data = self.database['request_forcesub']
        self.rqst_fsub_Channel_data = self.database['request_forcesub_channel']
        self.store_reqLink_data = self.database['store_reqLink']

        self.invite_expire_time_data = self.database['invite_expire_time']
        self.mask_button_data = self.database['mask_button']
    
    
    async def set_channel_button_link(self, button_name: str, button_link: str):
        await self.channel_button_link_data.delete_many({})
        await self.channel_button_link_data.insert_one({'button_name': button_name, 'button_link': button_link})
    
    async def get_channel_button_link(self):
        data = await self.channel_button_link_data.find_one({})
        if data:
            return data.get('button_name'), data.get('button_link')
        return 'Join Channel', 'https://t.me/Anime_Ocean_Official'
    
    async def set_del_timer(self, value: int):        
        existing = await self.del_timer_data.find_one({})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})
    
    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({})
        if data:
            return data.get('value', 600)
        return 600
    async def set_invite_expire_time(self, seconds: int):
        await self.invite_expire_time_data.delete_many({})
        await self.invite_expire_time_data.insert_one({'seconds': seconds})
        
    async def get_invite_expire_time(self):
        data = await self.invite_expire_time_data.find_one({})
        if data:
            return data.get('seconds', 0)
        return 0

    async def set_mask_button(self, button_name: str, button_link: str):
        await self.mask_button_data.delete_many({})
        if button_name and button_link:
            await self.mask_button_data.insert_one({'button_name': button_name, 'button_link': button_link})

    async def get_mask_button(self):
        data = await self.mask_button_data.find_one({})
        if data:
            return data.get('button_name'), data.get('button_link')
        return None, None

    async def set_auto_delete(self, value: bool):
        existing = await self.auto_delete_data.find_one({})
        if existing:
            await self.auto_delete_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.auto_delete_data.insert_one({'value': value})
    
    async def set_hide_caption(self, value: bool):
        existing = await self.hide_caption_data.find_one({})
        if existing:
            await self.hide_caption_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.hide_caption_data.insert_one({'value': value})
    
    async def set_protect_content(self, value: bool):
        existing = await self.protect_content_data.find_one({})
        if existing:
            await self.protect_content_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.protect_content_data.insert_one({'value': value})
    
    async def set_channel_button(self, value: bool):
        existing = await self.channel_button_data.find_one({})
        if existing:
            await self.channel_button_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.channel_button_data.insert_one({'value': value})
    
    async def set_request_forcesub(self, value: bool):
        existing = await self.rqst_fsub_data.find_one({})
        if existing:
            await self.rqst_fsub_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.rqst_fsub_data.insert_one({'value': value})
     
    
    async def get_auto_delete(self):
        data = await self.auto_delete_data.find_one({})
        if data:
            return data.get('value', False)
        return False
    
    async def get_hide_caption(self):
        data = await self.hide_caption_data.find_one({})
        if data:
            return data.get('value', False)
        return False
    
    async def get_protect_content(self):
        data = await self.protect_content_data.find_one({})
        if data:
            return data.get('value', False)
        return False
    
    async def get_channel_button(self):
        data = await self.channel_button_data.find_one({})
        if data:
            return data.get('value', False)
        return False
    
    async def get_request_forcesub(self):
        data = await self.rqst_fsub_data.find_one({})
        if data:
            return data.get('value', False)
        return False
    
    async def present_user(self, user_id : int):
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)
    
    async def add_user(self, user_id: int):
        await self.user_data.insert_one({'_id': user_id})
        return
    
    async def full_userbase(self):
        user_docs = await self.user_data.find().to_list(length=None)
        user_ids = []
        for doc in user_docs:
            user_ids.append(doc['_id'])
            
        return user_ids
    
    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})
        return
    
    async def channel_exist(self, channel_id: int):
        found = await self.channel_data.find_one({'_id': channel_id})
        return bool(found)
        
    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await self.channel_data.insert_one({'_id': channel_id})
            return
    
    async def del_channel(self, channel_id: int):
        if await self.channel_exist(channel_id):
            await self.channel_data.delete_one({'_id': channel_id})
            return
    
    async def get_all_channels(self):
        channel_docs = await self.channel_data.find().to_list(length=None)
        channel_ids = [doc['_id'] for doc in channel_docs]
        return channel_ids
    
    async def admin_exist(self, admin_id: int):
        found = await self.admins_data.find_one({'_id': admin_id})
        return bool(found)
        
    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await self.admins_data.insert_one({'_id': admin_id})
            return
    
    async def del_admin(self, admin_id: int):
        if await self.admin_exist(admin_id):
            await self.admins_data.delete_one({'_id': admin_id})
            return
    
    async def get_all_admins(self):
        users_docs = await self.admins_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids
    
    
    async def ban_user_exist(self, user_id: int):
        found = await self.banned_user_data.find_one({'_id': user_id})
        return bool(found)
        
    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({'_id': user_id})
            return
    
    async def del_ban_user(self, user_id: int):
        if await self.ban_user_exist(user_id):
            await self.banned_user_data.delete_one({'_id': user_id})
            return
    
    async def get_ban_users(self):
        users_docs = await self.banned_user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids
    

    async def add_reqChannel(self, channel_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$setOnInsert': {'user_ids': []}}, 
            upsert=True  
        )

    async def reqSent_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$addToSet': {'user_ids': user_id}}, 
            upsert=True
        )

    async def del_reqSent_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$pull': {'user_ids': user_id}}
        )
        
    async def clear_reqSent_user(self, channel_id: int):
        if await self.reqChannel_exist(channel_id):
            await self.rqst_fsub_Channel_data.update_one(
                {'_id': channel_id}, 
                {'$set': {'user_ids': []}}
            )

    async def reqSent_user_exist(self, channel_id: int, user_id: int):
        found = await self.rqst_fsub_Channel_data.find_one(
            {'_id': channel_id, 'user_ids': user_id}
        )
        return bool(found)
    async def del_reqChannel(self, channel_id: int):
        await self.rqst_fsub_Channel_data.delete_one({'_id': channel_id})

    async def reqChannel_exist(self, channel_id: int):
        found = await self.rqst_fsub_Channel_data.find_one({'_id': channel_id})
        return bool(found)

    async def get_reqSent_user(self, channel_id: int):
        data = await self.rqst_fsub_Channel_data.find_one({'_id': channel_id})
        if data:
            return data.get('user_ids', [])
        return []

    async def get_reqChannel(self):
        channel_docs = await self.rqst_fsub_Channel_data.find().to_list(length=None)
        channel_ids = [doc['_id'] for doc in channel_docs]
        return channel_ids
        
    async def get_reqLink_channels(self):
        channel_docs = await self.store_reqLink_data.find().to_list(length=None)
        channel_ids = [doc['_id'] for doc in channel_docs]
        return channel_ids

    async def get_stored_reqLink(self, channel_id: int):
        data = await self.store_reqLink_data.find_one({'_id': channel_id})
        if data:
            return data
        return None

    async def store_reqLink(self, channel_id: int, link: str, expire_at: int = None):
        update_data = {"link": link}
        if expire_at is not None:
            update_data["expire_at"] = expire_at
            
        await self.store_reqLink_data.update_one(
            {'_id': channel_id}, 
            {'$set': update_data}, 
            upsert=True
        )

    async def del_stored_reqLink(self, channel_id: int):
        await self.store_reqLink_data.delete_one({'_id': channel_id})

ocean = SidDataBase(DB_URI, DB_NAME)
