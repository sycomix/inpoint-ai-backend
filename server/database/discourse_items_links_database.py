import motor.motor_asyncio
from decouple import config
from bson.objectid import ObjectId

MONGO_INITDB_ROOT_USERNAME = config('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = config('MONGO_INITDB_ROOT_PASSWORD')
MONGO_CONTAINER_NAME = config('MONGO_CONTAINER_NAME')
MONGO_DETAILS = f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_CONTAINER_NAME}:27017'
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.inPOINT

discourse_items_links_collection = database.get_collection('discourseItemsLinks')


def discourse_items_link_from_database(discourse_items_link, client: str = 'frontend') -> dict:
    if client == 'frontend':
        return {
            'data': {
                'id': str(discourse_items_link['_id']),
                'sourceId': str(discourse_items_link['sourceId']),
                'targetId': str(discourse_items_link['targetId']),
                'type': discourse_items_link['type']
            }
        }
    elif client == 'ai':
        return {
            'id': str(discourse_items_link['_id']),
            'sourceId': str(discourse_items_link['sourceId']),
            'targetId': str(discourse_items_link['targetId']),
            'type': discourse_items_link['type']
        }


def discourse_items_link_for_database(discourse_items_link_data: dict, include_id: bool = False):
    discourse_items_link_data['sourceId'] = ObjectId(discourse_items_link_data['sourceId'])
    discourse_items_link_data['targetId'] = ObjectId(discourse_items_link_data['targetId'])
    if include_id:
        discourse_items_link_data['_id'] = ObjectId(discourse_items_link_data['_id'])
    return discourse_items_link_data


async def add_discourse_items_link(discourse_items_link_data: dict, include_id: bool = False):
    discourse_items_link_data = discourse_items_link_for_database(discourse_items_link_data, include_id)
    discourse_items_link = await discourse_items_links_collection.insert_one(discourse_items_link_data)
    new_discourse_items_link = await discourse_items_links_collection.find_one(
        {'_id': discourse_items_link.inserted_id})
    new_discourse_items_link_data = discourse_items_link_from_database(new_discourse_items_link)
    return new_discourse_items_link_data


async def retrieve_discourse_items_links():
    discourse_items_links = []
    async for discourse_items_link in discourse_items_links_collection.find():
        discourse_items_link_data = discourse_items_link_from_database(discourse_items_link)
        discourse_items_links.append(discourse_items_link_data)
    return discourse_items_links


async def retrieve_discourse_items_link(id: str, client: str = 'frontend') -> dict:
    discourse_items_link = await discourse_items_links_collection.find_one({'_id': ObjectId(id)})
    if discourse_items_link:
        discourse_items_link_data = discourse_items_link_from_database(discourse_items_link, client)
        return discourse_items_link_data


async def update_discourse_items_link(id: str, data: dict):
    if len(data) < 1:
        return False
    discourse_items_link = discourse_items_links_collection.find_one({'_id': ObjectId(id)})
    if not discourse_items_link:
        return False
    updated_discourse_items_link = await discourse_items_links_collection.update_one({'_id': ObjectId(id)},
                                                                                     {'$set': data})
    if updated_discourse_items_link:
        updated_discourse_items_link = await discourse_items_links_collection.find_one({'_id': ObjectId(id)})
        updated_discourse_items_link_data = discourse_items_link_from_database(updated_discourse_items_link)
        return updated_discourse_items_link_data
    return False


async def delete_discourse_items_link(id: str):
    discourse_items_link = await discourse_items_links_collection.find_one({'_id': ObjectId(id)})
    if discourse_items_link:
        await discourse_items_links_collection.delete_one({'_id': ObjectId(id)})
        return True
    return False
