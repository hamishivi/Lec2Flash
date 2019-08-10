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
    # trying some basic conditions for "inside:" what is/are?. What are seems
    # to work decently (ish) well.
    ## TODO: maybe flip them??
    question_gen_dict = {"'definition'":
                         "QUESTION:\n\tWhat is the definition of {}?\nANSWER:"
                         "\n\t{}\n",
                         "'inside'":
                         "QUESTION:\n\tWhat are {}?\nANSWER:\n\t{}\n"
                         }
    entities = []
    results = tx.run("MATCH (e1:Entity)-[r:Related]-> (e2:Entity) "
                     "RETURN e1.text as e1, e2.text as e2, r.text as rel")
    for record in results:
        entities.append((record["e1"], record["e2"], record["rel"]))
#     print(entities)

    for entry in entities:
        if entry[2] in question_gen_dict:
            print(question_gen_dict[entry[2]].format(entry[0], entry[1]))


all_types = []
with driver.session() as session:
    # all_types = session.read_transaction(get_all_relationship_types)
    session.read_transaction(make_match)
testing_all_types = []
for t in all_types:
    if t.startswith("VERB") or t.startswith("PREP"):
        continue
    testing_all_types.append(t)
print(sorted(testing_all_types))
