# nlp_graph.py

from neo4j import GraphDatabase

class GraphClient:
    def __init__(self, uri, user, password):
        # Initialize Neo4j driver
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Close the driver connection
        self.driver.close()

    def run_cypher(self, cypher, params=None):
        # Execute a Cypher query and return a list of record dicts
        with self.driver.session() as session:
            return [record.data() for record in session.run(cypher, params or {})]