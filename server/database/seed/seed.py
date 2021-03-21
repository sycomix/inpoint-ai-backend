import asyncio
import json
from typing import List

import motor.motor_asyncio
from decouple import config

from server.database.discourses_database import add_discourse

MONGO_INITDB_ROOT_USERNAME = config('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = config('MONGO_INITDB_ROOT_PASSWORD')
MONGO_URL = config('MONGO_URL')
MONGO_LOCALHOST_PORT = config('MONGO_LOCALHOST_PORT')
MONGO_DETAILS = f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_URL}:{MONGO_LOCALHOST_PORT}'
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.inPOINT
discourses_collection = database.get_collection('discourses')


async def _add_discourses(discourses: List[dict]):
    for discourse in discourses:
        print(f"Add seed discourse: {discourse['_id']}")
        await add_discourse(discourse, include_id=True)


async def main(seed_json_filepath):
    with open(seed_json_filepath) as f:
        data = json.load(f)
    await _add_discourses(data['discourses'])


if __name__ == '__main__':
    SEED_JSON_FILEPATH = 'server/database/seed/data.json'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(SEED_JSON_FILEPATH))
    loop.close()