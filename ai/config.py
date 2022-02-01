from decouple import config


# Initial Setup
debug = config('BACKEND_DEBUG', cast=bool)


# Connection data
BOLT_PORT = config('NEO4J_BOLT_PORT', cast=int)
NEO4J_URL = config('NEO4J_URL')
uri = f'bolt://{NEO4J_URL}:{BOLT_PORT}'
username = 'neo4j'
password = config('NEO4J_INITDB_ROOT_PASSWORD')


# Supported data types
node_types = ['Issue', 'Solution', 'Note', 'Position-against', 'Position-in-favor']
fields = ['UserId', 'id', 'SpaceId', 'UserId', 'Position', 'DiscussionText']
position_number_to_string = {
    -2: 'Solution',
    -1: 'Position-against',
    0: 'Note',
    1: 'Position-in-favor',
    2: 'Issue',
}


# Algorithmic values
cutoff = 0.5
top_n = 10
top_sent = 5
en_stopword_prefixes = ['and ', 'or ']
el_stopword_prefixes = ['και ', 'ή ']
