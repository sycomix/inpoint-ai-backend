from fastapi import APIRouter, Body, status
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from server.models.discourses import (Discourse, UpdateDiscourse)
from server.models.responses import ResponseModel, ErrorResponseModel
from server.database.discourses_database import (add_discourse, delete_discourse, retrieve_discourse, retrieve_discourses)

router = APIRouter()


@router.post('/', response_description='Discourse added into the database')
async def add_discourse_data(discourse_item: Discourse = Body(...)):
    discourse_data = jsonable_encoder(discourse_item)
    new_discourse = await add_discourse(discourse_data)
    if new_discourse:
        return ResponseModel.return_response(new_discourse, 'Discourse added successfully')
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_403_FORBIDDEN,
                                              f'The discourse couldn\'t be added')


@router.get('/', response_description='Discourses retrieved')
async def get_discourses():
    discourses = await retrieve_discourses()
    if discourses:
        return ResponseModel.return_response(discourses, 'Discourses retrieved successfully')
    return ResponseModel.return_response(discourses, 'Empty list')

@router.get('/{id}', response_description='Discourse retrieved')
async def get_discourse(id: str):
    discourse = await retrieve_discourse(id)
    if discourse:
        return ResponseModel.return_response(discourse, 'Discourse retrieved successfully')
    return ErrorResponseModel.return_response('An error occured', status.HTTP_404_NOT_FOUND,
                                              'Discourse doesn\'t exist')


@router.delete('/{id}', response_description='Discourse deleted')
async def delete_discourse_data(id: str):
    deleted_discourse = await delete_discourse(id)
    if deleted_discourse:
        return ResponseModel.return_response(f'Discourse with id: {id} removed',
                                             'Discourse deleted successfully')
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND,
                                              'Discourse doesn\'t exist')



