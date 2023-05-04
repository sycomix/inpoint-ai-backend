import sys
import logging
import datetime
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
from pymongo import MongoClient


@counter
def MLPipeline(en_nlp, el_nlp, lang_det, first_run = False):

    # Connect to the mongodb database.
    client = MongoClient(ai.config.mongo_connection_string)
    mongo_database = client['inpoint']
    
    # Throttle the use of the MLPipeline to once per hour.
    throttles_collection = mongo_database['throttles']
    res = throttles_collection.find_one()
    now = datetime.datetime.now()

    # Check if it not the first run 
    # and there is an entry to the throttle table to early return.
    if not first_run and res is not None:
        elapsed = now - res['date']
        if elapsed < datetime.timedelta(minutes = 59):
            warning = 'MLPipeline Throttling: Please try again later!'
            print(warning, file = sys.stderr)
            logging.warning(warning)
            return

    # Remove the old entry and save the current timestamp.
    throttles_collection.remove({})
    throttles_collection.insert_one({'date': now})

    # Connect to the neo4j database.
    database = Neo4jDatabase(ai.config.neo4j_connection_string, ai.config.neo4j_user, ai.config.neo4j_pwd)

    # Retrieve data from the Ergologic backend.
    # data json format: {'workspaces': [], 'discussions': []}
    try:
        results = ai.utils.get_data_from_ergologic()
        # If we have not received any results, early return.
        if results is None:
            return
        workspaces, discussions = results
    except Exception as e:
        logging.exception(e) # Log this exception and re-raise it for analyze.
        raise Exception(e)

    # Train the argument classifier from every text.
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

        # Suggest new argument types for each argument of each discussion in the current workspace.
        wsp_suggestions = ArgumentClassifier.suggest_argument_types(wsp_discussions, lang_det)

        # Sort similar arguments into clusters, and return their medoid text and summary.
        wsp_clusters = ArgumentClusterer.suggest_clusters(wsp_discussions, lang_det, en_nlp, el_nlp)

        # Create node groups from the discussions object.
        node_groups = \
            extract_node_groups(wsp_discussions, ai.config.node_types, ai.config.fields)

        # Create the discussion nodes in the Neo4j Database.
        create_discussion_nodes(database, node_groups)

        # Create the similarity graph.
        create_similarity_graph(
            database, node_groups, 
            en_nlp, el_nlp, lang_det, ai.config.cutoff
        )

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

    return


# Log all possible exceptions from the ML Pipeline.
def analyze(en_nlp, el_nlp, lang_det, first_run = False):
    try:
        MLPipeline(en_nlp, el_nlp, lang_det, first_run)
    except Exception as e:
        logging.exception(e)
    return


if __name__ == '__main__': analyze()
