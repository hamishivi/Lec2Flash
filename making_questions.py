from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j", "password"))

# Currently working on the finite set of relationships!!


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


def make_match(tx):
    question_gen_dict = {"'definition'":
                         "QUESTION:\n\tWhat is the definition of {}?\nANSWER:"
                         "\n\t{}\n"}
    word = "'definition'"  # TODO: maybe flip this. e.g. what's the word for x?
    entities = []
    results = tx.run("MATCH (e1:Entity)-[r:Related]-> (e2:Entity) "
                     "WHERE r.text=$text "
                     "RETURN e1.text as e1, e2.text as e2",
                     text=word)
    for record in results:
        entities.append((record["e1"], record["e2"]))
    print(entities)
    for pair in entities:
        print(question_gen_dict["'definition'"].format(pair[0], pair[1]))


all_types = []
with driver.session() as session:
    all_types = session.read_transaction(get_all_relationship_types)
    # session.read_transaction(make_match)
print(sorted(all_types))
