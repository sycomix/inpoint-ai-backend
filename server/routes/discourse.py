from typing import Union
from pydantic import Field
from fastapi import APIRouter, Body, status
from fastapi.encoders import jsonable_encoder
from server.models.discourses import (Discourse, UpdateDiscourseAddDiscourseItem, UpdateDiscourseAddDiscourseItemsLink,
                                      UpdateDiscourseDeleteDiscourseItemOrLink, Action, UpdateType)
from server.models.responses import ResponseModel, ErrorResponseModel
from server.database.discourses_database import (add_discourse, delete_discourse, retrieve_discourse,
                                                 retrieve_discourses, update_discourse, retrieve_discourse_ids)

router = APIRouter()


@router.post('/', response_description='Discourse added into the database')
async def add_discourse_data(discourseItem: Discourse = Body(...)):
    discourse_data = jsonable_encoder(discourseItem)
    new_discourse = await add_discourse(discourse_data)
    if new_discourse:
        return ResponseModel.return_response(new_discourse)
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_403_FORBIDDEN,
                                              f'The discourse couldn\'t be added')


@router.get('/frontend', response_description='Discourses retrieved for frontend')
async def get_discourses_frontend():
    client = 'frontend'
    discourses = await retrieve_discourses(client)
    if discourses:
        return ResponseModel.return_response(discourses)
    return ResponseModel.return_response({'message': 'Empty List'})


@router.get('/ai', response_description='Discourses retrieved for frontend')
async def get_discourses_frontend():
    client = 'ai'
    discourses = await retrieve_discourses(client)
    if discourses:
        return ResponseModel.return_response(discourses)
    return ResponseModel.return_response({'message': 'Empty List'})


@router.get('/ids', response_description='Discourses retrieved')
async def get_discourse_ids():
    discourses = await retrieve_discourse_ids()
    if discourses:
        return ResponseModel.return_response(discourses)
    return ResponseModel.return_response({'message': 'Empty List'})


@router.get('/{id}/frontend', response_description='Discourse retrieved')
async def get_discourse(id: str):
    client = 'frontend'
    discourse = await retrieve_discourse(id, client)
    if discourse:
        return ResponseModel.return_response(discourse)
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND,
                                              'Discourse doesn\'t exist')


@router.get('/{id}/ai', response_description='Discourse retrieved')
async def get_discourse(id: str):
    client = 'ai'
    discourse = await retrieve_discourse(id, client)
    if discourse:
        return ResponseModel.return_response(discourse)
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND,
                                              'Discourse doesn\'t exist')


@router.delete('/{id}', response_description='Discourse deleted')
async def delete_discourse_data(id: str):
    deleted_discourse = await delete_discourse(id)
    if deleted_discourse:
        return ResponseModel.return_response({'message': f'Discourse with id: {id} removed'})
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND,
                                              'Discourse doesn\'t exist')


@router.put('/{id}', response_description='Discourse updated')
async def update_discourse_data(id: str, action: Action, update_type: UpdateType,
                                data: Union[UpdateDiscourseAddDiscourseItem, UpdateDiscourseAddDiscourseItemsLink,
                                            UpdateDiscourseDeleteDiscourseItemOrLink] = Body(...)):
    if action == 'add':
        if isinstance(data, UpdateDiscourseDeleteDiscourseItemOrLink):
            return ErrorResponseModel.return_response('An error occurred', status.HTTP_403_FORBIDDEN,
                                                      'Expected UpdateDiscourseAddDiscourseItem with action=add!')
    elif isinstance(
        data,
        (
            UpdateDiscourseAddDiscourseItem,
            UpdateDiscourseAddDiscourseItemsLink,
        ),
    ):
        return ErrorResponseModel.return_response('An error occurred', status.HTTP_403_FORBIDDEN,
                                                  'Expected UpdateDiscourseDeleteDiscourseItem with action=delete!')
    discourse_data = jsonable_encoder(data)
    updated_discourse = await update_discourse(id, action, update_type, discourse_data)
    if updated_discourse:
        if type(updated_discourse) != bool:
            return ResponseModel.return_response(updated_discourse)
        else:
            return ResponseModel.return_response({'message': 'The whole discourse was deleted'})
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND,
                                              'There was an error updating the discourse data')
