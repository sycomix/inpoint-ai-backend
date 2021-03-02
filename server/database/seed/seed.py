import json
import motor.motor_asyncio
from server.database.discourses_database import add_discourse

async def seed_database(seed_json_filepath):
    with open(seed_json_filepath) as f:
        data = json.load(f)
    for discourse in data['discourses']:
        await add_discourse(discourse)