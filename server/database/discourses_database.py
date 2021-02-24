import motor.motor_asyncio
from decouple import config
from bson.objectid import ObjectId

from server.database.discourse_items_database import delete_discourse_item, add_discourse_item, retrieve_discourse_item

MONGO_DETAILS = config('MONGO_DETAILS')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.inPOINT

discourses_collection = database.get_collection('discourses_collection')


async def discourse_helper(discourse) -> dict:
    discourse_items_ids = list(discourse['discourse_items'])
    discourse_items_data =[]
    for discourse_item_id in discourse_items_ids:
        discourse_item_data=await retrieve_discourse_item(str(discourse_item_id))
        discourse_items_data.append(discourse_item_data)
    return {
        'id': str(discourse['_id']),
        'discourse_items': discourse_items_data
    }


async def discourse_insert_discourse_items(discourse_data: dict):
    discourse_items_data = discourse_data['discourse_items']
    discourse_items_ids =[]
    for discourse_item_data in discourse_items_data:
        discourse_item = await add_discourse_item(discourse_item_data)
        discourse_items_ids.append(ObjectId(discourse_item['id']))
    discourse_data['discourse_items'] = discourse_items_ids
    return discourse_data


async def discourse_delete_discourse_items(discourse):
    discourse_items_ids = list(discourse['discourse_items'])
    for discourse_item_id in discourse_items_ids:
        if not await delete_discourse_item(discourse_item_id):
            return False
    return True


async def retrieve_discourses():
    discourses = []
    async for discourse in discourses_collection.find():
        discourse_data = await discourse_helper(discourse)
        discourses.append(discourse_data)
    return discourses


async def retrieve_discourse(id: str):
    discourse = await discourses_collection.find_one({'_id': ObjectId(id)})
    if discourse:
        discourse_data = await discourse_helper(discourse)
        return discourse_data


async def add_discourse(discourse_data):
    discourse_data = await discourse_insert_discourse_items(discourse_data)
    discourse = await discourses_collection.insert_one(discourse_data)
    new_discourse = await discourses_collection.find_one({'_id':discourse.inserted_id})
    new_discourse_data = await discourse_helper(new_discourse)
    return new_discourse_data


# WE MUST DEFINE WHAT UPDATE HERE ACTUALLY MEANS BECAUSE IT CAN MEAN EITHER DELETE A DISCOURSE_ITEM
# OR ADD A DISCOURSE_ITEM OR A BUNCH OF THEM
# async def update_discourse(id: str, data:dict):
#     if len(data) < 1:
#         return False
#     discourse = discourses_collection.find_one({'_id': ObjectId(id)})
#     if not discourse:
#         return False
#     if data['purpose'] == 'add':
#         discourse_item = await add_discourse_item(data['discourse_item'])
#         discourse_items_ids = list(discourse['discourse_items'])
#         discourse_items_ids.append(ObjectId(discourse_item['id']))
#         updated_discourse = await discourses_collection.update_one({'_id': ObjectId(id)},{'$set':{'discourse_items': discourse_items_ids}})
#         updated_discourse = await discourses_collection.update_one({'_id':id}, )
#         if updated_discourse:
#             updated_discourse = await discourses_collection.find_one({'_id': id})
#             updated_discourse_data = discourse_helper(updated_discourse)
#             return updated_discourse_data
#     if data['purpose'] == 'delete':
#
#         discourse_item=await delete_discourse_item(data['discourse_item'])
#     return False


async def delete_discourse(id: str):
    discourse = await discourses_collection.find_one({'_id': ObjectId(id)})
    if discourse:
        if await discourse_delete_discourse_items(discourse):
            await discourses_collection.delete_one({'_id': ObjectId(id)})
            return True
    return False
