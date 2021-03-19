from fastapi import APIRouter, Body, status
from fastapi.encoders import jsonable_encoder
from server.models.discourse_items_links import DiscourseItemsLink, UpdateDiscourseItemsLink
from server.models.responses import ResponseModel, ErrorResponseModel
from server.database.discourse_items_links_database import (add_discourse_items_link, retrieve_discourse_items_links,
                                                            retrieve_discourse_items_link, update_discourse_items_link,
                                                            delete_discourse_items_link)


router = APIRouter()


@router.post('/', response_description='Discourse items link added into the database')
async def add_discourse_items_link_data(discourse_items_link: DiscourseItemsLink = Body(...)):
    discourse_items_link_data = jsonable_encoder(discourse_items_link)
    new_discourse_items_link = await add_discourse_items_link(discourse_items_link_data)
    if new_discourse_items_link:
        return ResponseModel.return_response(new_discourse_items_link)
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_403_FORBIDDEN,
                                              'The discourse items link couldn\'t be added')


@router.get('/', response_description='Discourse items links retrieved')
async def get_discourse_items_links():
    discourse_items_links = await retrieve_discourse_items_links()
    if discourse_items_links:
        return ResponseModel.return_response(discourse_items_links)
    return ResponseModel.return_response({'message': 'Empty list'})


@router.get('/{id}', response_description='Discourse item link retrieved')
async def get_discourse_items_link(id: str):
    discourse_items_link = await retrieve_discourse_items_link(id)
    if discourse_items_link:
        return ResponseModel.return_response(discourse_items_link)
    return ErrorResponseModel.return_response('An error occured', status.HTTP_404_NOT_FOUND,
                                              'Discourse items link doesn\'t exist')


@router.put('/{id}', response_description='Discourse items link updated')
async def update_discourse_items_link_data(id: str, data: UpdateDiscourseItemsLink = Body(...)):
    data = {key: value for key, value in data.dict().items() if value is not None}
    updated_discourse_items_link = await update_discourse_items_link(id, data)
    if updated_discourse_items_link:
        return ResponseModel.return_response(updated_discourse_items_link)
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND,
                                              'There was an error updating the discourse items link data')


@router.delete('/{id}', response_description='Discourse item link deleted')
async def delete_discourse_items_data(id: str):
    deleted_discourse_items_link = await delete_discourse_items_link(id)
    if deleted_discourse_items_link:
        return ResponseModel.return_response({'message': f'Discourse items link with id: {id} removed'})
    return ErrorResponseModel.return_response('An error occurred', status.HTTP_404_NOT_FOUND,
                                              'Discourse item link doesn\'t exist')
