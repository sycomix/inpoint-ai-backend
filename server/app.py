from fastapi import FastAPI
from app.server.routes.user import router as UserRouter

app = FastAPI()

app.include_router(UserRouter, tags=['Users'], prefix='/user')

@app.get('/', tags=['Root'])
async def read_root():
    return {'message': 'Welcome to this fantastic app!'}
