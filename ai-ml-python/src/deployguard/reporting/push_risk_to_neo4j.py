import os
from neo4j import GraphDatabase


class Neo4jRiskWriter:

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "neo4j123")

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )

    def close(self):
        self.driver.close()

    def push_risk(self, risk_data: dict):
        """
        Push risk scores to Neo4j.

        Args:
            risk_data (dict): {service_name: risk_score}
        """
        with self.driver.session() as session:
            for service, risk in risk_data.items():
                session.execute_write(self._update_risk, service, risk)

    @staticmethod
    def _update_risk(tx, service_name, risk_score):
        tx.run(
            """
            MERGE (s:Service {name: $name})
            SET s.risk = $risk
            """,
            name=service_name,
            risk=risk_score
        )
