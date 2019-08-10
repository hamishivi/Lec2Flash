from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j", "password"))


def _read_example_inputs():
    input_file = "sample_output.txt"
    split_opt = "', "
    with open(input_file, "r") as f:
        examples = [line.rstrip()[1:-1].split(split_opt) for line in f]
    return examples


def add_entity(tx, data):
    """ ASSUMPTIONS:
        no duplicate tuples
    """
    print(data)
    # Extract whatever info to store here
    entity1, entity2, relationship = data
    tx.run("MERGE (e1:Entity {text: $text1}) "
           "MERGE (e2:Entity {text: $text2}) "
           "MERGE (e1)-[:Related{text: $text_rel}]->(e2)",
           text1=entity1, text2=entity2, text_rel=relationship)


with driver.session() as session:
    for i in _read_example_inputs():
        session.write_transaction(add_entity, i)
