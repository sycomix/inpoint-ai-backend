import logging
from decouple import config


# Initial Setup
debug = config('BACKEND_DEBUG', cast = bool)


# Basic config logger of the backend.
logging.basicConfig(
    filename = 'inpoint_backend.logs', encoding = 'utf-8', 
    filemode = 'a', datefmt = '%H:%M:%S', level = logging.INFO, force = True,
    format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
)


# Credentials for neo4j and mongodb.
neo4j_user = config('NEO4J_INITDB_ROOT_USERNAME')
neo4j_pwd = config('NEO4J_INITDB_ROOT_PASSWORD')
bolt_port = config('NEO4J_BOLT_PORT', cast = int)
neo4j_url = config('NEO4J_URL')
neo4j_connection_string = f'bolt://{neo4j_url}:{bolt_port}'

mongo_user = config('MONGO_INITDB_ROOT_USERNAME')
mongo_pwd = config('MONGO_INITDB_ROOT_PASSWORD')
mongo_port = config('MONGO_LOCALHOST_PORT')
mongo_url = config('MONGO_URL')
mongo_connection_string = f'mongodb://{mongo_user}:{mongo_pwd}@{mongo_url}:{mongo_port}'


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
