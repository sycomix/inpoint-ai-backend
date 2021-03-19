import motor.motor_asyncio
from decouple import config
from bson.objectid import ObjectId

from server.database.discourse_items_database import delete_discourse_item, add_discourse_item, retrieve_discourse_item
from server.database.discourse_items_links_database import (delete_discourse_items_link, add_discourse_items_link,
                                                            retrieve_discourse_items_link)

MONGO_INITDB_ROOT_USERNAME = config('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = config('MONGO_INITDB_ROOT_PASSWORD')
MONGO_CONTAINER_NAME = config('MONGO_CONTAINER_NAME')
MONGO_DETAILS = f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_CONTAINER_NAME}:27017'
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.inPOINT

discourses_collection = database.get_collection('discourses')


async def discourse_from_database(discourse, client: str = 'frontend') -> dict:
    discourse_items_ids = list(discourse['discourseItems'])
    discourse_items_data = []
    for discourse_item_id in discourse_items_ids:
        discourse_item_data = await retrieve_discourse_item(str(discourse_item_id), client)
        discourse_items_data.append(discourse_item_data)

    discourse_items_links_ids = list(discourse['discourseItemsLinks'])
    discourse_items_links_data = []
    for discourse_items_links_id in discourse_items_links_ids:
        discourse_items_link_data = await retrieve_discourse_items_link(str(discourse_items_links_id), client)
        discourse_items_links_data.append(discourse_items_link_data)
    if client == 'frontend':
        results = {
            'id': str(discourse['_id']),
            'data': discourse_items_data + discourse_items_links_data
        }
        # results = [{'id': str(discourse['_id'])}]
        # results = results + discourse_items_data + discourse_items_links_data
    elif client == 'ai':
        results = {
            'id': str(discourse['_id']),
            'nodes': discourse_items_data,
            'edges': discourse_items_links_data
        }
    return results


async def discourse_add_discourse_items_and_links(discourse_data: dict, include_id: bool = False):
    discourse_items_data = discourse_data['discourseItems']
    discourse_items_ids = []
    for discourse_item_data in discourse_items_data:
        discourse_item = await add_discourse_item(discourse_item_data, include_id)
        discourse_items_ids.append(ObjectId(discourse_item['data']['id']))
    discourse_data['discourseItems'] = discourse_items_ids

    discourse_items_links_data = discourse_data['discourseItemsLinks']
    discourse_items_links_ids = []
    for discourse_items_links_data in discourse_items_links_data:
        discourse_items_link = await add_discourse_items_link(discourse_items_links_data, include_id)
        discourse_items_links_ids.append(ObjectId(discourse_items_link['data']['id']))
    discourse_data['discourseItemsLinks'] = discourse_items_links_ids
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


async def update_discourse_add_discourse_items_link(discourse, discourse_data: dict):
    discourse_items_link = await add_discourse_items_link(discourse_data['discourseItemsLink'])
    discourse_items_links_ids = list(discourse['discourseItemsLinks'])
    discourse_items_links_ids.append(ObjectId(discourse_items_link['data']['id']))
    updated_discourse = await discourses_collection.update_one({'_id': discourse['_id']}, {
        '$set': {'discourseItemsLinks': discourse_items_links_ids}})
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


async def update_discourse_delete_discourse_items_link(discourse, discourse_data: dict):
    discourse_items_links_ids = list(discourse['discourseItemsLinks'])
    if ObjectId(discourse_data['id']) not in discourse_items_links_ids:
        return False
    if await delete_discourse_items_link(discourse_data['id']):
        discourse_items_links_ids.remove(ObjectId(discourse_data['id']))
        # if not discourse_items_links_ids_ids:
        #     await discourses_collection.delete_one({'_id':discourse['_id']})
        #     return True
        updated_discourse = await discourses_collection.update_one({'_id': discourse['_id']}, {
            '$set': {'discourseItemsLinks': discourse_items_links_ids}})
        if updated_discourse:
            new_discourse = await discourses_collection.find_one({'_id': discourse['_id']})
            if new_discourse:
                new_discourse_data = await discourse_from_database(new_discourse)
                return new_discourse_data
    return False


async def discourse_delete_discourse_items_and_links(discourse):
    discourse_items_ids = list(discourse['discourseItems'])
    for discourse_item_id in discourse_items_ids:
        if not await delete_discourse_item(discourse_item_id):
            return False

    discourse_items_links_ids = list(discourse['discourseItemsLinks'])
    for discourse_items_link_id in discourse_items_links_ids:
        if not await delete_discourse_items_link(discourse_items_link_id):
            return False
    return True


async def retrieve_discourses(client: str):
    discourses = []
    async for discourse in discourses_collection.find():
        discourse_data = await discourse_from_database(discourse, client)
        discourses.append(discourse_data)
    return discourses


async def retrieve_discourse_ids():
    discourse_ids = [str(discourse['_id']) async for discourse in discourses_collection.find()]
    return discourse_ids


async def retrieve_discourse(id: str, client: str):
    discourse = await discourses_collection.find_one({'_id': ObjectId(id)})
    if discourse:
        discourse_data = await discourse_from_database(discourse, client)
        return discourse_data


async def add_discourse(discourse_data, include_id: bool = False):
    discourse_data = await discourse_add_discourse_items_and_links(discourse_data, include_id)

    if include_id:
        discourse_data['_id'] = ObjectId(discourse_data['_id'])
    discourse = await discourses_collection.insert_one(discourse_data)
    new_discourse = await discourses_collection.find_one({'_id': discourse.inserted_id})
    new_discourse_data = await discourse_from_database(new_discourse)
    return new_discourse_data


async def update_discourse(id: str, action: str, update_type: str, discourse_data: dict):
    if len(discourse_data) < 1:
        return False
    discourse = await discourses_collection.find_one({'_id': ObjectId(id)})
    if not discourse:
        return False
    if action == 'add':
        if update_type == 'discourseItem':
            new_discourse_data = await update_discourse_add_discourse_item(discourse, discourse_data)
        else:
            new_discourse_data = await update_discourse_add_discourse_items_link(discourse, discourse_data)
        return new_discourse_data
    if action == 'delete':
        if update_type == 'discourseItem':
            new_discourse_data = await update_discourse_delete_discourse_item(discourse, discourse_data)
        else:
            new_discourse_data = await update_discourse_delete_discourse_items_link(discourse, discourse_data)
        return new_discourse_data
    return False


async def delete_discourse(id: str):
    discourse = await discourses_collection.find_one({'_id': ObjectId(id)})
    if discourse:
        discourse_items_ids = list(discourse['discourseItems'])
        discourse_items_links_ids = list(discourse['discourseItemsLinks'])
        if discourse_items_ids or discourse_items_links_ids:
            if await discourse_delete_discourse_items_and_links(discourse):
                return await discourses_collection.delete_one({'_id': ObjectId(id)})
            return False
        else:
            return await discourses_collection.delete_one({'_id': ObjectId(id)})
    return False
