import sys
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

class Neo4jDatabase(object): 
    """
    Wrapper class which handles the Neo4j  
    database driver by abstracting repeating code.
    """
    def __init__(self, uri, user, password): # Create the database connection.
        self.driver = GraphDatabase.driver(uri, auth = (user, password))

    def close(self):
        self.driver.close()

    def execute(self, query, mode): # Execute a query using a database session.
        with self.driver.session() as session:
            result = None
            try:
                 result = session.run(query)
                 if (mode in 'rw'): # Read / Write query.
                    result = result.values()
                 elif(mode == 'g'): # Graph data query.
                    result = result.data()
                 else:
                    raise TypeError('Execution mode can either be (r)ead, (w)rite or (g)raph data!')
            except Neo4jError as err:
                print(err, file = sys.stderr) # Print the error instead of breaking the execution.
        return result
