from typer import Argument
from fastapi import FastAPI, Request
from fastapi import Query
from py2neo import Graph
from fastapi import status
from decouple import config
from pymongo import MongoClient
from typing import List
from server.models.responses import ErrorResponseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import ai.config
import ai.utils
from ai.utils import counter
from ai.neo4j_wrapper import (
    Neo4jDatabase, 
    GraphAlgos
)
from ai.select import (
    summarize_communities,
    aggregate_summaries_keyphrases
)
from ai.create import (
    extract_node_groups,
    create_discussion_nodes,
    create_similarity_graph
)

from ai.classification import ArgumentClassifier


app = FastAPI(docs_url='/docs', redoc_url=None)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

en_nlp, el_nlp, lang_det = ai.utils.Models.load_models()

MONGO_INITDB_ROOT_USERNAME = config('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = config('MONGO_INITDB_ROOT_PASSWORD')
MONGO_URL = config('MONGO_URL')
MONGO_LOCALHOST_PORT = config('MONGO_LOCALHOST_PORT')
MONGO_CONNECTION_STRING = f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_URL}:{MONGO_LOCALHOST_PORT}'


@app.get('/', tags=['Root'])
async def read_root():
    return {'message': 'Welcome to the Main back-end!'}


@app.get('/get-analysis', tags=['Root'])
async def get_analysis(q: List[int] = Query(...)):
    workspace_ids = q
    client = MongoClient(MONGO_CONNECTION_STRING)
    mongo_database = client['inpoint']
    workspaces_collection = mongo_database['workspaces']
    workspaces = workspaces_collection.find({'_id': {'$in': workspace_ids}})

    # If there are no workspaces, return early.
    if workspaces is None:
        not_found_response = {}
        return JSONResponse(content=not_found_response, status_code=404)

    return {'workspaces': list(workspaces)}


@app.post('/analyze', tags=['Root'])
async def analyze(request: Request):
    # Allow only localhost calls.
    ip = str(request.client.host)
    if not ip in ['172.20.0.1', '127.0.0.1']:
        data = {
            'message': f'IP {ip} is not allowed to access this resource.'
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    # Connect to the database.
    database = Neo4jDatabase(ai.config.uri, ai.config.username, ai.config.password)
    graph = Graph(ai.config.uri, auth = (ai.config.username, ai.config.password))

    # Retrieve data from the Ergologic backend.
    # data json format: {'workspaces': [], 'discussions': []}
    try:
        workspaces, discussions = ai.utils.get_data_from_ergologic()
    except Exception as e:
        return ErrorResponseModel.return_response(
            str(e), status.HTTP_500_INTERNAL_SERVER_ERROR,
            'Failed to communicate properly with the ergologic endpoint!'
        )

    # Train the argument classifier from all texts.
    ArgumentClassifier.train_classifiers(discussions, lang_det)

    # Each workspace will hold a list of results.
    results = []

    for wsp in workspaces:
        # Delete the entire workspace graph.
        database.execute('MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r', 'w')

        # Only include discussions that match the current workspace.
        wsp_discussions = [
            discussion for discussion in discussions 
            if discussion['SpaceId'] == wsp['id']
        ]

        # Suggest new argument types for each discussion in the current workspace.
        wsp_suggestions = ArgumentClassifier.suggest_labels(wsp_discussions, lang_det)

        # Create node groups from the discussions object.
        node_groups = \
            extract_node_groups(wsp_discussions, ai.config.node_types, ai.config.fields)

        # Create the discussion nodes in the Neo4j Database.
        create_discussion_nodes(graph, node_groups, ai.config.fields)

        # Create the similarity graph.
        create_similarity_graph(graph, node_groups, 
                            ai.config.node_types, ai.config.fields, 
                            en_nlp, el_nlp, lang_det, ai.config.cutoff)

        # Calculate the community score for the similarity graph.
        with GraphAlgos(database, ['Node'], ['is_similar']) as similarity_graph:
            similarity_graph.louvain(write_property = 'community')

        # Group summaries based on their node types.
        node_groups = {node: {'Summaries': []}
                      for node in ai.config.node_types if node != 'Issue'}

        # Summarize each community of discussions and group them based on their position.
        for id, [position, _, summary] in summarize_communities(
                                                      database, en_nlp, el_nlp, 
                                                      lang_det, ai.config.top_n, 
                                                      ai.config.top_sent).items():   
            node_groups[position]['Summaries'].append(summary)

        # Produce an aggregated summary and keyphrases.
        aggregated = aggregate_summaries_keyphrases(
            node_groups, lang_det, en_nlp, el_nlp, ai.config.top_n, ai.config.top_sent
        )
        
        # Each workspace is a dict object, which contains
        # its id, text summaries grouped by node (argument)
        # type, an aggregated summary and a list of keyphrases.
        results.append({'_id': wsp['id'], **aggregated, **node_groups, **wsp_suggestions})

    # Connect to MongoDB, delete older summaries & keyphrases
    # from all workspaces and insert the newly created ones.
    client = MongoClient(MONGO_CONNECTION_STRING)
    mongo_database = client['inpoint']
    workspaces_collection = mongo_database['workspaces']
    workspaces_collection.remove({})
    workspaces_collection.insert_many(results)

    return results