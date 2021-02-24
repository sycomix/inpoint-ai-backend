from fastapi import APIRouter, Body, status
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from server.models.discourse_items import (DiscourseItem, UpdateDiscourseItem)
from server.models.responses import ResponseModel, ErrorResponseModel
from server.database.discourse_items_database import (
add_discourse_item,
update_discourse_item,
delete_discourse_item,
retrieve_discourse_items,
retrieve_discourse_item
)


def discourse_item_helper(discourse_item: DiscourseItem = Body(...)) -> dict:
    discourse_item_data = jsonable_encoder(discourse_item)
    discourse_item_data['userId'] = ObjectId(discourse_item_data['userId'])
    if discourse_item_data['parentId'] is not None:
        discourse_item_data['parentId'] = ObjectId(discourse_item_data['parentId'])
    return discourse_item_data


router = APIRouter()


@router.post('/', response_description='Discourse item added into the database')
async def add_discourse_item_data(discourse_item: DiscourseItem = Body(...)):
    discourse_item_data = discourse_item_helper(discourse_item)
    new_discourse_item = await add_discourse_item(discourse_item_data)
    if new_discourse_item:
        return ResponseModel.return_response(new_discourse_item, 'Discourse item added successfully')
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_403_FORBIDDEN,
                                              f'The discourse item couldn\'t be added')


@router.get('/', response_description='Discourse items retrieved')
async def get_discourse_items():
    discourse_items = await retrieve_discourse_items()
    if discourse_items:
        return ResponseModel.return_response(discourse_items, 'Discourse items retrieved successfully')
    return ResponseModel.return_response(discourse_items, 'Empty list')


@router.get('/{id}', response_description='Discourse item retrieved')
async def get_discourse_item(id: str):
    discourse_item = await retrieve_discourse_item(id)
    if discourse_item:
        return ResponseModel.return_response(discourse_item, 'Discourse item retrieved successfully')
    return ErrorResponseModel.return_response('An error occured', status.HTTP_404_NOT_FOUND,
                                              'Discourse item doesn\'t exist')


@router.put('/{id}')
async def update_discourse_item_data(id: str, data: UpdateDiscourseItem = Body(...)):
    data = {key: value for key, value in data.dict().items() if value is not None}
    updated_discourse_item = await update_discourse_item(id, data)
    if updated_discourse_item:
        return ResponseModel.return_response({'updated discourse item':updated_discourse_item,
                                              'message':f'Update of discourse item with id: {id} is successful'},
                                             'User data updated successfully')
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND,
                                             'There was an error updating the user data')


@router.delete('/{id}', response_description='Discourse item deleted')
async def delete_discourse_item_data(id: str):
    deleted_discourse_item = await delete_discourse_item(id)
    if deleted_discourse_item:
        return ResponseModel.return_response(f'Discourse Item with id: {id} removed',
                                             'Discourse item deleted successfully')
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND,
                                              'Discourse item doesn\'t exist')
