from neo4j import GraphDatabase
import pandas as pd

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j","neo4j123"))

risk_data = {
    "order":0.136393,
    "payment":0.136224,
    "inventory":0.000102
}

def push(tx, name, risk):
    tx.run("""
    MATCH (s:Service {name:$name})
    SET s.risk=$risk
    """, name=name, risk=risk)

with driver.session() as session:
    for k,v in risk_data.items():
        session.write_transaction(push,k,v)

driver.close()
