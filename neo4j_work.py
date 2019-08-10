from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j", "password"))


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


# get all the relationships types
def get_all_relationship_types(tx):
    r_types = []
    results = tx.run("MATCH (e1:Entity)-[r:Related]-> (e2:Entity)"
                     "RETURN r.text as text")
    for record in results:
        r_type = record["text"][1:-1]
        if r_type not in r_types:
            r_types.append(r_type)
    return r_types

# TODO: make this better by not including the entities that are parents of other entities.
# this would eliminate headings -> subheadings
def make_match_inside(tx):
    word = "inside" 
    entities = []
    results = tx.run("MATCH (e1:Entity)-[r:Related]-> (e2:Entity) "
                     "WHERE r.text=$text "
                     "RETURN e1.text as e1, e2.text as e2",
                     text=word)
    for record in results:
        entities.append((record["e1"], record["e2"]))
    qs = []
    for pair in entities:
        qs.append(
            {
                "QUESTION": "Name a {}?".format(pair[1]),
                "ANSWER": "{}".format(pair[0])
            })
    return qs

def make_match_definition(tx):
    word = "definition" 
    entities = []
    results = tx.run("MATCH (e1:Entity)-[r:Related]-> (e2:Entity) "
                     "WHERE r.text=$text "
                     "RETURN e1.text as e1, e2.text as e2",
                     text=word)
    for record in results:
        entities.append((record["e1"], record["e2"]))
    qs = []
    for pair in entities:
        qs.append(
            {
                "QUESTION": "What is the definition of {}?".format(pair[0]),
                "ANSWER": "{}".format(pair[1])
            })
    return qs

def wipeout(tx):
    tx.run("MATCH (n) DETACH DELETE n")

if __name__ == "__main__":
    all_types = []
    with driver.session() as session:
        all_types = session.read_transaction(get_all_relationship_types)
        # session.read_transaction(make_match)
    print(sorted(all_types))
