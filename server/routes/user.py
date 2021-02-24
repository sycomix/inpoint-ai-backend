from fastapi import APIRouter, Body, status
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from server.database.users_database import (add_user, delete_user, retrieve_users, retrieve_user, update_user, change_password)
from server.models.users import (User, UpdateUserModel, ChangePasswordModel)
from server.models.responses import (ResponseModel, ErrorResponseModel)

router = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post('/', response_description='User data added into the database')
async def add_user_data(user: User = Body(...)):
    user = jsonable_encoder(user)
    password = user['password']
    user.pop('password')
    user['hashed_password'] = pwd_context.hash(password)
    new_user = await add_user(user)
    if new_user:
        return ResponseModel.return_response(new_user, 'User added successfully')
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_403_FORBIDDEN,
                                              f'The username {user["username"]} is not available!')


@router.get('/', response_description='Users retrieved')
async def get_users():
    users = await retrieve_users()
    if users:
        return ResponseModel.return_response(users, 'Users data retrieved successfully')
    return ResponseModel.return_response(users, 'Emplty list returned')


@router.get('/{username}', response_description='User data retrieved')
async def get_student_data(username: str):
    user = await retrieve_user(username)
    if user:
        return ResponseModel.return_response(user, 'User data retrieved successfully')
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND, 'User doesn\'t exist')


@router.put('/{username}')
async def update_user_data(username: str, req: UpdateUserModel = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_user = await update_user(username, req)
    if updated_user:
        return ResponseModel.return_response({'updated user': updated_user,
                                              'message': f'User with past username: {username} update is successful'},
                                             'User data updated successfully')
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND,
                                              'There was an error updating the user data')


@router.delete('/{username}')
async def delete_user_data(username: str):
    deleted_user = await delete_user(username)
    if deleted_user:
        return ResponseModel.return_response(f'User with ID: {username} removed', 'User deleted successfully')
    return ErrorResponseModel.return_response(
            'An error occurred',
            status.HTTP_404_NOT_FOUND,
            f'User with ID: {username} doesn\'t exist')


@router.put('/{username}/change_password')
async def change_user_password(username: str, password: ChangePasswordModel = Body(...)):
    password = jsonable_encoder(password)
    password = password['password']
    hashed_password = pwd_context.hash(password)
    updated_user = await change_password(username, hashed_password)
    if updated_user:
        return ResponseModel.return_response(f'Password changed for user with username {username}',
                                             'Password changed successfully')
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND, 'User doesn\'t exist')