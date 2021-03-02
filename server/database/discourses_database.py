import motor.motor_asyncio
from decouple import config
from bson.objectid import ObjectId

from server.database.discourse_items_database import delete_discourse_item, add_discourse_item, retrieve_discourse_item

MONGO_INITDB_ROOT_USERNAME = config('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = config('MONGO_INITDB_ROOT_PASSWORD')
MONGO_CONTAINER_NAME = config('MONGO_CONTAINER_NAME')
MONGO_DETAILS = f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_CONTAINER_NAME}:27017'
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.inPOINT

discourses_collection = database.get_collection('discourses')


async def discourse_from_database(discourse) -> dict:
    discourse_items_ids = list(discourse['discourseItems'])
    discourse_items_data = []
    for discourse_item_id in discourse_items_ids:
        discourse_item_data = await retrieve_discourse_item(str(discourse_item_id))
        discourse_items_data.append(discourse_item_data)
    return {
        'id': str(discourse['_id']),
        'discourseItems': discourse_items_data
    }


async def discourse_add_discourse_items(discourse_data: dict):
    discourse_items_data = discourse_data['discourseItems']
    discourse_items_ids = []
    for discourse_item_data in discourse_items_data:
        discourse_item = await add_discourse_item(discourse_item_data)
        discourse_items_ids.append(ObjectId(discourse_item['data']['id']))
    discourse_data['discourseItems'] = discourse_items_ids
    return discourse_data


async def update_discourse_add_discourse_item(discourse, discourse_data: dict):
    discourse_item = await add_discourse_item(discourse_data['discourseItem'])
    discourse_items_ids = list(discourse['discourseItems'])
    discourse_items_ids.append(ObjectId(discourse_item['data']['id']))
    updated_discourse = await discourses_collection.update_one({'_id': discourse['_id']},
                                                               {'$set': {'discourseItems': discourse_items_ids}})
    if updated_discourse:
        new_discourse = await discourses_collection.find_one({'_id': discourse['_id']})
        if new_discourse:
            new_discourse_data = await discourse_from_database(new_discourse)
            return new_discourse_data
    return False


async def update_discourse_delete_discourse_item(discourse, discourse_data: dict):
    discourse_items_ids = list(discourse['discourseItems'])
    if ObjectId(discourse_data['id']) not in discourse_items_ids:
        return False
    if await delete_discourse_item(discourse_data['id']):
        discourse_items_ids.remove(ObjectId(discourse_data['id']))
        if not discourse_items_ids:
            await discourses_collection.delete_one({'_id': discourse['_id']})
            return True
        updated_discourse = await discourses_collection.update_one({'_id': discourse['_id']},
                                                                   {'$set': {'discourseItems': discourse_items_ids}})
        if updated_discourse:
            new_discourse = await discourses_collection.find_one({'_id': discourse['_id']})
            if new_discourse:
                new_discourse_data = await discourse_from_database(new_discourse)
                return new_discourse_data
    return False


async def discourse_delete_discourse_items(discourse):
    discourse_items_ids = list(discourse['discourseItems'])
    for discourse_item_id in discourse_items_ids:
        if not await delete_discourse_item(discourse_item_id):
            return False
    return True


async def retrieve_discourses():
    discourses = []
    async for discourse in discourses_collection.find():
        discourse_data = await discourse_from_database(discourse)
        discourses.append(discourse_data)
    return discourses


async def retrieve_discourse(id: str):
    discourse = await discourses_collection.find_one({'_id': ObjectId(id)})
    if discourse:
        discourse_data = await discourse_from_database(discourse)
        return discourse_data


async def add_discourse(discourse_data):
    discourse_data = await discourse_add_discourse_items(discourse_data)
    discourse = await discourses_collection.insert_one(discourse_data)
    new_discourse = await discourses_collection.find_one({'_id': discourse.inserted_id})
    new_discourse_data = await discourse_from_database(new_discourse)
    return new_discourse_data


async def update_discourse(id: str, discourse_data:dict):
    if len(discourse_data) < 1:
        return False
    discourse = await discourses_collection.find_one({'_id': ObjectId(id)})
    if not discourse:
        return False
    if discourse_data['purpose'] == 'add':
        new_discourse_data = await update_discourse_add_discourse_item(discourse, discourse_data)
        return new_discourse_data
    if discourse_data['purpose'] == 'delete':
        new_discourse_data = await update_discourse_delete_discourse_item(discourse, discourse_data)
        return new_discourse_data
    return False


async def delete_discourse(id: str):
    discourse = await discourses_collection.find_one({'_id': ObjectId(id)})
    if discourse:
        discourse_items_ids = list(discourse['discourseItems'])
        if discourse_items_ids:
            if await discourse_delete_discourse_items(discourse):
                return await discourses_collection.delete_one({'_id':ObjectId(id)})
            return False
        else:
            return await discourses_collection.delete_one({'_id':ObjectId(id)})
    return False
