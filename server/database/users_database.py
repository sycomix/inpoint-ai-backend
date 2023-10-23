import motor.motor_asyncio
from decouple import config

MONGO_DETAILS = config('MONGO_DETAILS')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.inPOINT

user_collection = database.get_collection('users')


def user_helper(user) -> dict:
    return {
        'id': str(user['_id']),
        'username': user['username'],
        'hashed_password': user['hashed_password'],
        'email': user['email'],
        'full_name': user['full_name'],
        'disabled': user['disabled']
    }


async def retrieve_users():
    users = []
    async for user in user_collection.find():
        user_data = user_helper(user)
        user_data.pop('hashed_password')
        users.append(user_data)
    return users


async def add_user(user_data: dict):
    check = await user_collection.find_one({'username': user_data['username']})
    if not check:
        user = await user_collection.insert_one(user_data)
        new_user = await user_collection.find_one({'_id': user.inserted_id})
        new_user_data = user_helper(new_user)
        new_user_data.pop('hashed_password')
        return new_user_data


async def retrieve_user(username: str) -> dict:
    user = await user_collection.find_one({'username': username})
    if user:
        user_data = user_helper(user)
        user_data.pop('hashed_password')
        return user_data


async def update_user(username: str, data: dict):
    if not data:
        return False
    if 'hashed_password' in data:
        return False
    user = await user_collection.find_one({'username': username})
    if not user:
        return False
    updated_user = await user_collection.update_one({'username': username}, {'$set': data})
    if updated_user:
        if 'username' in data:
            updated_user = await user_collection.find_one({'username': data['username']})
        else:
            updated_user = await user_collection.find_one({'username': username})
    if updated_user:
        updated_user_data = user_helper(updated_user)
        updated_user_data.pop('hashed_password')
        return updated_user_data
    return False


async def delete_user(username: str):
    user = await user_collection.find_one({'username': username})
    if user:
        await user_collection.delete_one({'username': username})
        return True
    return False


async def change_password(username: str, hashed_password: str):
    if not hashed_password:
        return False
    user = await user_collection.find_one({'username': username})
    if not user:
        return False
    updated_user = await user_collection.update_one(
        {'username': username},
        {'$set': {
            'hashed_password': hashed_password
        }
        }
    )
    return bool(updated_user)
