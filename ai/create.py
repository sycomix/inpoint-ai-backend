import json
from bs4 import BeautifulSoup
from py2neo.bulk import create_nodes, merge_relationships
from ai.similarity import calc_similarity_pairs
from ai.utils import counter

@counter
def extract_node_groups(discussions, node_types, fields):
    """
    Function that extracts the node groups
    in-memory objects from the discussion object.
    """

    # This dictionary separates different types of nodes.
    node_groups = {
        k: [] 
        for k in node_types
    }

    # Iterate all discussion objects, and append each one in the node group.
    for discussion in discussions:
        node_groups[discussion['Position']].append({
            field: discussion.get(field)
            for field in fields
        })      
    return node_groups

@counter
def create_discussion_nodes(database, node_groups, fields):
    """
    Function that creates each node in the database.
    """
    # Create a unique constraint and merge all nodes of each node group.
    for label, nodes in node_groups.items():
        try:
            database.schema.create_uniqueness_constraint(label, 'id')
        except:
            pass
        if nodes: # Create nodes, if the collection is not empty.
            create_nodes(database.auto(), nodes, labels = {'Node', label})
    return

@counter
def create_similarity_graph(database, node_groups, node_types, fields, 
                            en_nlp, el_nlp, lang_det, cutoff):
    """
    Function that creates the similarity subgraph in the database,
    between the discussion nodes created earlier.
    """
    
    # This dictionary separates different types of nodes.
    # This part assumes that there is only one issue node.
    # That's the reason we skip it.

    node_groups_similarity_pairs = {
        k: [] 
        for k in [
            node_type
            for node_type in node_types
            if node_type != 'Issue'
        ]
    }

    # Calculate all node groups similarity pairs.
    for label, nodes in node_groups.items():
        if label == 'Issue':
            continue

        # Create the list of texts and ids for all nodes of a specific type.
        text_ids = [(node['id'], node['DiscussionText']) for node in nodes]

        # We need at least two texts to make the comparison.
        if len(text_ids) < 2:
            continue
        else:
            edges = \
                calc_similarity_pairs(text_ids, en_nlp, el_nlp, lang_det, cutoff)

            # Convert the similarity score to a dict, for the call below.
            edges = [(source, {'score': score}, target) for source, score, target in edges]

            # Merge all relationships, depending on source, target id, if they exist.
            if edges:
                merge_relationships(
                    database.auto(), edges, merge_key = ('is_similar', 'score'),
                    start_node_key = ('Node', 'id'), end_node_key = ('Node', 'id'))

    return
