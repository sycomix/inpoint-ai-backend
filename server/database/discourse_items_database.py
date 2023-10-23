import motor.motor_asyncio
from decouple import config
from bson.objectid import ObjectId

MONGO_INITDB_ROOT_USERNAME = config('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = config('MONGO_INITDB_ROOT_PASSWORD')
MONGO_URL = config('MONGO_URL')
MONGO_LOCALHOST_PORT = config('MONGO_LOCALHOST_PORT')
MONGO_DETAILS = f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_URL}:{MONGO_LOCALHOST_PORT}'
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.inPOINT

discourse_items_collection = database.get_collection('discourseItems')


def discourse_item_from_database(discourse_item, client: str = 'frontend') -> dict:
    if client == 'frontend':
        return {
                'group': 'nodes',
                'data': {
                    'id': str(discourse_item['_id']),
                    'label': discourse_item['label'],
                    'type': discourse_item['type'],
                    'text': discourse_item['text'],
                    'authorId': str(discourse_item['authorId']),
                    'likes': discourse_item['likes'],
                    'dislikes': discourse_item['dislikes'],
                    'createdAt': discourse_item['_id'].generation_time.strftime('%Y-%m-%d %H:%M:%S')
                }
        }
    elif client == 'ai':
        return {
            'id': str(discourse_item['_id']),
            'label': discourse_item['label'],
            'type': discourse_item['type'],
            'text': discourse_item['text'],
            'authorId': str(discourse_item['authorId']),
            'likes': discourse_item['likes'],
            'dislikes': discourse_item['dislikes'],
            'createdAt': discourse_item['_id'].generation_time.strftime('%Y-%m-%d %H:%M:%S')
        }


# The objectID for every discourse item must be a 12-letter string with only hex digits (0123456789abcdef) Else,
# we must use a different type for the _id field such as plain string, integer etc. In this case we will lose
# createdAt value.
def discourse_item_for_database(discourse_item_data: dict, include_id: bool = False) -> dict:
    discourse_item_data['authorId'] = ObjectId(discourse_item_data['authorId'])
    if include_id:
        discourse_item_data['_id'] = ObjectId(discourse_item_data['_id'])
    return discourse_item_data


async def add_discourse_item(discourse_item_data: dict, include_id: bool = False):
    discourse_item_data = discourse_item_for_database(discourse_item_data, include_id)
    discourse_item = await discourse_items_collection.insert_one(discourse_item_data)
    new_discourse_item = await discourse_items_collection.find_one({'_id': discourse_item.inserted_id})
    return discourse_item_from_database(new_discourse_item)


async def retrieve_discourse_items():
    discourse_items = []
    async for discourse_item in discourse_items_collection.find():
        discourse_item_data = discourse_item_from_database(discourse_item)
        discourse_items.append(discourse_item_data)
    return discourse_items


async def retrieve_discourse_item(id: str, client: str = 'frontend') -> dict:
    discourse_item = await discourse_items_collection.find_one({'_id': ObjectId(id)})
    if discourse_item:
        return discourse_item_from_database(discourse_item, client)


async def update_discourse_item(id: str, data: dict):
    if not data:
        return False
    discourse_item = discourse_items_collection.find_one({'_id': ObjectId(id)})
    if not discourse_item:
        return False
    updated_discourse_item = await discourse_items_collection.update_one({'_id': ObjectId(id)}, {'$set': data})
    if updated_discourse_item:
        updated_discourse_item = await discourse_items_collection.find_one({'_id': ObjectId(id)})
        return discourse_item_from_database(updated_discourse_item)
    return False


async def delete_discourse_item(id: str):
    discourse_item = await discourse_items_collection.find_one({'_id': ObjectId(id)})
    if discourse_item:
        await discourse_items_collection.delete_one({'_id': ObjectId(id)})
        return True
    return False
