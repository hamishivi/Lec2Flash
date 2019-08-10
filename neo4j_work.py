from neo4j import GraphDatabase
from spacy.lemmatizer import Lemmatizer
import language_check
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
import spacy

lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
nlp = spacy.load("en_core_web_lg")
tool = language_check.LanguageTool('en-US')

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j", "password"))


# some nice utils for dealing with text.
# this doesnt really make singular, rather it lemmatizes things
# but for nouns this is essentially the same.
# doesnt work for 'protasis' and 'apodosis' 
#   turns them into 'protasi' and 'apodosi'...
def make_singular(text):
    doc = nlp(text)
    s = ''
    for token in doc:
        if token.pos_ == "NOUN":
            s += f"{lemmatizer(token.text, token.pos_)[0]} "
        else:
            s += token.text + ' '
    return s.strip()

# this is to check for the common pattern: "are <VERB>" and remove them
# these are common due to how we are creating questions
def remove_are_verb(text):
    doc = nlp(text)
    for idx, token in enumerate(doc):
        if token.text == "are":
            if doc[idx+1].pos_ == "VERB":
                return text.replace("What are", "What")
    return text

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

# this changes the entire grammar... but it can be wrong! alot!
# so use with caution...
def full_grammar_check(text):
    matches = tool.check(text)
    return language_check.correct(text, matches)

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
        elif entry[2].startswith("VERB: "):
            qs.append({"QUESTION":
                       question_gen_dict["VERB: "]["QUESTION"].format(
                            entry[0], entry[2][len("VERB: "):]),
                       "ANSWER":
                       question_gen_dict["VERB: "]["ANSWER"].format(
                           entry[1])
                       }
                      )
        elif entry[2].startswith("PREP: "):
            # TODO: all the prep entries seem pretty broken tbh
            continue
    # quick clean-up
    for q in qs:
        q["QUESTION"] = remove_are_verb(q["QUESTION"])
        if 'What is the definition of' in q["QUESTION"]:
            q["QUESTION"] = make_singular(q["QUESTION"])
    return qs


def wipeout(tx):
    tx.run("MATCH (n) DETACH DELETE n")


if __name__ == "__main__":
    with driver.session() as session:
        session.read_transaction(make_match)
