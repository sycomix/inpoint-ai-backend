import ai.config
from typing import List
from fastapi import FastAPI
from fastapi import Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient


app = FastAPI(docs_url = '/docs', redoc_url = None)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["GET"],
    allow_headers = ["*"],
)


# Default endpoint for testing the availability of the server.
@app.get('/', tags = ['Root'])
async def read_root():
    return {'message': 'Welcome to the inPOINT AI backend!'}


# The endpoint which serves the results of the AI Analysis from MongoDB.
@app.get('/get-analysis', tags = ['Root'])
async def get_analysis(q: List[int] = Query(...)):
    workspace_ids = q
    client = MongoClient(ai.config.mongo_connection_string)
    mongo_database = client['inpoint']
    workspaces_collection = mongo_database['workspaces']
    workspaces = workspaces_collection.find({'_id': {'$in': workspace_ids}})

    # If there are no workspaces, return early.
    if workspaces is None:
        not_found_response = {}
        return JSONResponse(content = not_found_response, status_code = 404)

    return {'workspaces': list(workspaces)}
