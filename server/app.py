import datetime
from fastapi import FastAPI, Request
from fastapi import Query
from py2neo import Graph
from fastapi import status
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
from ai.clustering import ArgumentClusterer


app = FastAPI(docs_url='/docs', redoc_url=None)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Load models.
en_nlp, el_nlp, lang_det = ai.utils.Models.load_models()


@app.get('/', tags=['Root'])
async def read_root():
    return {'message': 'Welcome to the Main back-end!'}


@app.get('/get-analysis', tags=['Root'])
async def get_analysis(q: List[int] = Query(...)):
    workspace_ids = q
    client = MongoClient(ai.config.mongo_connection_string)
    mongo_database = client['inpoint']
    workspaces_collection = mongo_database['workspaces']
    workspaces = workspaces_collection.find({'_id': {'$in': workspace_ids}})

    # If there are no workspaces, return early.
    if workspaces is None:
        not_found_response = {}
        return JSONResponse(content=not_found_response, status_code=404)

    return {'workspaces': list(workspaces)}

# Analyze can only run once per hour.
@app.post('/analyze', tags=['Root'])
async def analyze(request: Request):
    # Connect to the mongodb database.
    client = MongoClient(ai.config.mongo_connection_string)
    mongo_database = client['inpoint']
    throttles_collection = mongo_database['throttles']
    res = throttles_collection.find_one()
    now = datetime.datetime.now()
    if res is not None:
        elapsed = now - res['date']
        if elapsed < datetime.timedelta(minutes=60):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                'message': 'Analyze has recently run. Please try again later!'
                })
    throttles_collection.remove({})
    throttles_collection.insert_one({'date': now})

    # Allow only localhost calls.
    ip = str(request.client.host)
    if ip.split('.', 1)[0] not in {'172', '192', '127'}:
        data = {
            'message': f'IP {ip} is not allowed to access this resource.'
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    # Connect to the neo4j database.
    database = Neo4jDatabase(ai.config.neo4j_connection_string, ai.config.neo4j_user, ai.config.neo4j_pwd)
    graph = Graph(ai.config.neo4j_connection_string, auth = (ai.config.neo4j_user, ai.config.neo4j_pwd))

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
    ArgumentClusterer.fit_clusterers(discussions, lang_det)

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
        wsp_clusters = ArgumentClusterer.suggest_clusters(wsp_discussions, lang_det)

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
        results.append({'_id': wsp['id'], **aggregated, **node_groups, **wsp_suggestions, **wsp_clusters})

    # Delete older summaries & keyphrases
    # from all workspaces and insert the newly created ones.
    workspaces_collection = mongo_database['workspaces']
    workspaces_collection.remove({})
    workspaces_collection.insert_many(results)

    return results