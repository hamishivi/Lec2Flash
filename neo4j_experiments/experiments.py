from neo4j import GraphDatabase

example_inputs = [["Keswick", "English market town", "is a"],
                  ["Edward I", "Keswick", "ruled"],
                  ["Edward I", "England", "of"],
                  ["River Greta", "river", "is"],
                  ["River Greta", "Cumbria England", "in"],
                  ["River Greta", "River Derwent", "tribuary"],
                  ["Greta", "stony stream", "Name in old Norse"],
                  ["River Greta", "River Derwent", "connects to"]
                  ]


driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j", "password"))


def add_entity_test(tx, data):
    """ ASSUMPTIONS:
        no duplicate tuples
    """
    # Extract whatever info to store here
    entity1, entity2, relationship = data

    tx.run("MERGE (e1:Entity {text: $text1}) "
           "MERGE (e2:Entity {text: $text2}) "
           "MERGE (e1)-[:Related{text: $text_rel}]->(e2)",
           text1=entity1, text2=entity2, text_rel=relationship)


with driver.session() as session:
    for i in example_inputs:
        session.write_transaction(add_entity_test, i)
    session.write_transaction(add_entity_test, ["e1b", "e2b", "r"])
