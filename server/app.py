from fastapi import FastAPI
from server.routes.user import router as UserRouter
from server.routes.discourse_item import router as DiscourseItemRouter
from server.routes.discourse import router as DiscourseRouter

app = FastAPI()

app.include_router(UserRouter, tags=['Users'], prefix='/users')
app.include_router(DiscourseItemRouter, tags=['Discourse Items'], prefix='/discourse_items')
app.include_router(DiscourseRouter, tags=['Discourses'], prefix='/discourses')

@app.get('/', tags=['Root'])
async def read_root():
    return {'message': 'Welcome to this fantastic app!'}
