from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j", "password"))


def add_entity(tx, data):
    """ ASSUMPTIONS:
        no duplicate tuples
    """
    # Extract whatever info to store here
    entity1, entity2, relationship = data
    tx.run("MERGE (e1:Entity {text: $text1}) "
           "MERGE (e2:Entity {text: $text2}) "
           "MERGE (e1)-[:Related{text: $text_rel}]->(e2)",
           text1=entity1, text2=entity2, text_rel=relationship)


def make_match(tx):
    # trying some basic conditions for "inside:" what is/are?. What are seems
    #   to work decently (ish) well.
    # trying some basic stuff for verbs. Currently is <question> <verb> <what>.
    #   sometimes where would be better fitted though
    # TODO: maybe flip them??
    question_gen_dict = {"definition":
                         {"QUESTION": "What is the definition of {}?",
                          "ANSWER": "{}"},
                         "inside":
                         {"QUESTION": "What are {}?",
                          "ANSWER": "{}"},
                         "VERB: ":
                         {"QUESTION": "{} {} what?",
                          "ANSWER": "{}"}
                         }
    results = tx.run("MATCH (e1:Entity)-[r:Related]-> (e2:Entity) "
                     "RETURN e1.text as e1, e2.text as e2, r.text as rel")
    entities = [(record["e1"], record["e2"], record["rel"])
                for record in results]
    qs = []
    for entry in entities:
        if entry[2] in question_gen_dict:
            qs.append({"QUESTION":
                       question_gen_dict[entry[2]]["QUESTION"].format(
                           entry[0]),
                       "ANSWER":
                       question_gen_dict[entry[2]]["ANSWER"].format(
                           entry[1])
                       }
                      )
        elif entry[2].startswith("'VERB: "):
            qs.append({"QUESTION":
                       question_gen_dict[entry[2]]["QUESTION"].format(
                            entry[0], entry[2][len("VERB: "):]),
                       "ANSWER":
                       question_gen_dict[entry[2]]["ANSWER"].format(
                           entry[1])
                       }
                      )
    return qs


def wipeout(tx):
    tx.run("MATCH (n) DETACH DELETE n")


if __name__ == "__main__":
    with driver.session() as session:
        session.read_transaction(make_match)
