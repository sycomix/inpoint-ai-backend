from fastapi import FastAPI
# from server.routes.user import router as UserRouter
from server.routes.discourse_item import router as DiscourseItemRouter
from server.routes.discourse import router as DiscourseRouter
from server.routes.discourse_items_link import router as DiscourseItemsLinkRouter
import server.utils as utils

app = FastAPI(docs_url='/api/docs', redoc_url=None)

# app.include_router(UserRouter, tags=['Users'], prefix='/users')
app.include_router(DiscourseItemRouter, tags=['Discourse Items'], prefix='/api/discourse_items')
app.include_router(DiscourseRouter, tags=['Discourses'], prefix='/api/discourses')
app.include_router(DiscourseItemsLinkRouter, tags=['Discourse Items Links'], prefix='/api/discourse_items_links')


@app.get('/', tags=['Root'])
async def read_root():
    return {'message': 'Welcome to the Main back-end!'}


@app.get('/api/demo/seed', tags=['Seed'])
async def seed_database():
    from server.database.seed import seed
    await seed.main('server/database/seed/data.json')
    return {'message': 'OK!'}

@app.get('/api/retrieve_data', tags=['Root'])
async def retrieve_data():
    workspaces, discussions = utils.get_data_from_ergologic()
    # call ai back-end
    return {'message': 'UPAT back-end updated'}