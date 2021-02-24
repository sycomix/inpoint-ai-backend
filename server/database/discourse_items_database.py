import motor.motor_asyncio
from decouple import config
from bson.objectid import ObjectId

MONGO_DETAILS = config('MONGO_DETAILS')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.inPOINT

discourse_items_collection = database.get_collection('discourse_items_collection')


def discourse_item_helper(discourse_item) -> dict:
    return {
        'id': str(discourse_item['_id']),
        'userId': str(discourse_item['userId']),
        'text': discourse_item['text'],
        'createdAt': discourse_item['_id'].generation_time.strftime('%Y-%m-%d %H:%M:%S'),
        'parentId': str(discourse_item['parentId']) if discourse_item['parentId'] else None
    } if discourse_item['parentId'] else {
        'id':str(discourse_item['_id']),
        'userId':str(discourse_item['userId']),
        'text':discourse_item['text'],
        'createdAt':discourse_item['_id'].generation_time.strftime('%Y-%m-%d %H:%M:%S')
    }


async def retrieve_discourse_items():
    discourse_items = []
    async for discourse_item in discourse_items_collection.find():
        discourse_item_data = discourse_item_helper(discourse_item)
        discourse_items.append(discourse_item_data)
    return discourse_items


async def add_discourse_item(discourse_item_data: dict):
    discourse_item = await discourse_items_collection.insert_one(discourse_item_data)
    new_discourse_item = await discourse_items_collection.find_one({'_id':discourse_item.inserted_id})
    new_discourse_item_data = discourse_item_helper(new_discourse_item)
    return new_discourse_item_data


async def retrieve_discourse_item(id: str) -> dict:
    discourse_item = await discourse_items_collection.find_one({'_id': ObjectId(id)})
    if discourse_item:
        discourse_item_data = discourse_item_helper(discourse_item)
        return discourse_item_data


async def update_discourse_item(id:str, data:dict):
    if len(data) < 1:
        return False
    discourse_item = discourse_items_collection.find_one({'_id': ObjectId(id)})
    if not discourse_item:
        return False
    updated_discourse_item = await discourse_items_collection.update_one({'_id':ObjectId(id)},{'$set': data})
    if updated_discourse_item:
        updated_discourse_item = await discourse_items_collection.find_one({'_id':ObjectId(id)})
        updated_discourse_item_data = discourse_item_helper(updated_discourse_item)
        return updated_discourse_item_data
    return False


async def delete_discourse_item(id: str):
    discourse_item = await discourse_items_collection.find_one({'_id': ObjectId(id)})
    if discourse_item:
        await discourse_items_collection.delete_one({'_id': ObjectId(id)})
        return True
    return False