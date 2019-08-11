import spacy
import re
from typing import List, Tuple

nlp = spacy.load("en_core_web_lg")

def load_file(filename: str) -> List[str]:
    """
    Helper function for loading a file.
    """
    with open(filename, 'r') as f:
        return f.readlines()

# basic definition checker
def check_def_line(line: str, symbol: str) -> List[str]:
    """
    Checks if a line of text contains a definition
    """
    split_line = line.split(symbol)
    if (len(split_line) == 2 and split_line[0] and split_line[1]):
        return [(line.split(symbol)[0].strip(), line.split(symbol)[1].strip(), "definition")]
    return []

def dot_points(lines: List[str]) -> Tuple[List[str], int]:
    relations = []
    stack = []
    cur_indent = 0
    lines = [l.replace("*", " ") for l in lines]
    for idx, line in enumerate(lines):
        indentation = len(line) - len(line.lstrip())
        # clear stack if at indent 0
        if indentation == 0:
            cur_indent = 0
            stack = []
        if indentation > cur_indent:
            stack.append(lines[idx-1])
            cur_indent = indentation
        elif indentation < cur_indent:
            cur_indent = indentation
            if len(stack) > 0:
                stack.pop()
        if len(stack) > 0 and stack[-1]:
            relations.append((line, stack[-1], 'inside'))
    return relations

def extract_defn_pattern(line: str) -> List[str]:
    """
    Extracts definition relations.
    """
    relations = []
    relations += check_def_line(line, "= ")
    relations += check_def_line(line, "- ")
    relations += check_def_line(line, ": ")
    return relations

def extract_verb_relations(text: str) -> List[str]:
    """
    Extract relations between verb and sentence
    """
    relations = []
    doc = nlp(text)
    for token in doc:
        if 'subj' in token.dep_:
            verb_idx = 0
            for idx, sent_tok in enumerate(token.head.sent):
                if sent_tok.text == token.head.text:
                    verb_idx = idx
            sent_a = " ".join([t.text for t in token.head.sent[:verb_idx]])
            sent_b = " ".join([t.text for t in token.head.sent[verb_idx+1:]])
            relations.append((sent_a, sent_b, f"VERB: {token.head.text}"))
    return relations

def extract_preposition_relations(text: str) -> List[str]:
    """
    Extract prepositions and their objects
    """
    doc = nlp(text)
    relations = []
    for token in doc.noun_chunks:
        if token.root.dep_ == "pobj" and token.root.head.dep_ == "prep":
            relations.append((" ".join([t.text for t in token.sent]), token.text.strip(), f"PREP: {token.root.head.text}"))
    return relations

def cleanup(relations: List[str]) -> List[str]:
    """
    Clean up text.
    """
    for idx, r in enumerate(relations):
        a, b, c = r
        # remove star
        a = a.replace('\n', "")
        b = b.replace('\n', "")
        c = c.replace('\n', "")
        a = re.sub('[\*\-\"\'“]', "", a).strip()
        b = re.sub('[\*\-\"\'“]', "", b).strip()
        c = re.sub('[\*\-\"\'“]', "", c).strip()
        a = a.lower()
        b = b.lower()
        c = c.lower()
        relations[idx] = (a, b, c)
    # remove relations that aren;t good for questions
    clean_relations = []
    for r in relations:
        a, b, c = r
        if '(' in a or ')' in a or 'e.g' in a or len(a) > 150 or len(a.strip()) == 0:
            continue
        if '(' in b or ')' in b or 'e.g' in b or len(b) > 150 or len(b.strip()) == 0:
            continue
        clean_relations.append(r)
    return clean_relations

def get_relations(text: str, text_as_lines: List[str]) -> List[str]:
    """
    Extracts relations from text as a whole.
    """
    relations = []
    # get dot point facts
    relations += dot_points([l for l in text_as_lines])
    # defns
    for l in text_as_lines:
        relations += extract_defn_pattern(l)
    # verbs
    relations += extract_verb_relations(text)
    # prepositions
    relations += extract_preposition_relations(text)
    # filter empty relations
    relations = [r for r in relations if r[0] and r[1] and r[2]]
    relations = cleanup(relations)
    return relations

if __name__ == "__main__":
    lines = load_file('notes.txt')
    text = "\n".join(lines)
    for r in get_relations(text, lines):
        print(r)
