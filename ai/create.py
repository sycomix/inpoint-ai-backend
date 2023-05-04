from ai.similarity import calc_similarity_pairs


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


def create_discussion_nodes(database, node_groups):
    """
    Function that creates each node in the database.
    """
    # Create a unique constraint and merge all nodes of each node group.
    for label, nodes in node_groups.items():
        try:
            query = (
                f'CREATE CONSTRAINT ON (node:Node) '
                'ASSERT node.id IS UNIQUE'
            )
            database.execute(query, 'w')
        except:
            pass
        if nodes: # Create (or Merge) nodes, if the collection is not empty.
            # Construct the neo4j list of dictionaries string.
            string_builder, single_quote = '[', '\''
            for node in nodes:
                item = ', '.join(f'{k}: {v if type(v) == int else single_quote+v+single_quote}' for k, v in node.items())
                string_builder += f'{{{item}}}, '
            list_of_dicts = string_builder[:-2] + ']'

            query = (
                f'UNWIND {list_of_dicts} AS node '
                f'MERGE (n:Node {{UserId: node.UserId, id: node.id, '
                f'SpaceId: node.SpaceId, Position: node.Position, '
                f'DiscussionText: node.DiscussionText}})'
            )
            database.execute(query, 'w')
    return


def create_similarity_graph(database, node_groups, 
                            en_nlp, el_nlp, lang_det, cutoff):
    """
    Function that creates the similarity subgraph in the database,
    between the discussion nodes created earlier.
    """
    
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
            edges = [[source, score, target] for source, score, target in edges]

            # Merge all relationships, depending on source, target id, if they exist.
            if edges:
                query = (
                    f'UNWIND {edges} as row '
                    'MATCH (s:Node {id: row[0]}), (t:Node{id: row[2]}) '
                    'MERGE (s)-[r:is_similar]-(t) '
                    'SET r.score = row[1]'
                )
                database.execute(query, 'w')

    return
