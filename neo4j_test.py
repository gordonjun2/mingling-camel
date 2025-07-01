from neo4j import GraphDatabase
from config import (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

print(driver.verify_connectivity())

with driver.session() as session:
    result = session.run("RETURN 1")
    print(result.single())
