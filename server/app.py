import sys
import json
import requests

from decouple import config
from fastapi import FastAPI
from fastapi import status
from fastapi import Request
from py2neo import Graph

import ai.config
import ai.utils

from server.models.responses import (ResponseModel, ErrorResponseModel)
from server.routes.event import router as EventRouter
# from server.routes.user import router as UserRouter
from server.routes.discourse_item import router as DiscourseItemRouter
from server.routes.discourse import router as DiscourseRouter
from server.routes.discourse_items_link import router as DiscourseItemsLinkRouter
import server.utils as utils

from ai.neo4j_wrapper import Neo4jDatabase
from ai.graph_algos import GraphAlgos
from ai.utils import counter
from ai.select import summarize_communities
from ai.create import (
    extract_node_groups,
    create_discussion_nodes,
    create_similarity_graph
)



AI_BACKEND_URL = config('AI_BACKEND_URL')

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

    # Call AI back-end
    try:
        res = requests.post(f'{AI_BACKEND_URL}/analyze', json={'workspaces': workspaces, 'discussions':discussions})
    except requests.exceptions.RequestException as e:
        return ErrorResponseModel.return_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                  'Failed to communicate with the ai back-end application!')
    if res.status_code == 200:
        json_data = res.json()
    else:
        return ErrorResponseModel.return_response(f'{res.text}, {res.status_code}', status.HTTP_424_FAILED_DEPENDENCY,
                                                  'Failed to communicate with the ai back-end application!')

    return json_data



MAIN_BACKEND_URL = config('MAIN_BACKEND_URL')
en_nlp, el_nlp, lang_det = ai.utils.Models.load_models()

app = FastAPI()

app.include_router(EventRouter, tags=['Event'], prefix='/events')


@app.post('/analyze', tags=['Root'])
async def analyze_data(request: Request):
    # Connect to the database.
    database = Neo4jDatabase(ai.config.uri, ai.config.username, ai.config.password)
    graph = Graph(ai.config.uri, auth = (ai.config.username, ai.config.password))

    # Retrieve data from the Ergologic backend.
    # data json format: {'workspaces': [], 'discussions': []}
    json_object = await request.json()
    workspaces, discussions = json_object['workspaces'], json_object['discussions']
    
    # Each workspace will hold a list of results.
    results = {wsp['id']: None for wsp in workspaces}

    for wsp in workspaces:
        # Delete the entire workspace graph.
        database.execute('MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r', 'w')

        # Only include discussions that match the current workspace.
        wsp_discussions = [
            discussion for discussion in discussions 
            if discussion['SpaceId'] == wsp['id']
        ]

        # Create node groups from the wsp_discussions object.
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

        # Group results based on their node types.
        node_groups = {k: [] for k in ai.config.node_types if k != 'Issue'}

        # Summarize each community of discussions and group them based on their position.
        for id, [position, _, summary, keyphrases] in summarize_communities(
                                                      database, en_nlp, el_nlp, 
                                                      lang_det, ai.config.top_n, 
                                                      ai.config.top_sent).items():   
            node_groups[position].append({
                'Summary': summary,
                'Keyphrases': keyphrases
            })
        
        # Assign the node groups to the specific workspace.
        results[wsp['id']] = node_groups
    return results