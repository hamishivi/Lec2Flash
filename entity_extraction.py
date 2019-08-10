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

def dot_points(lines: List[str], cur_line: int, cur_indent: int, head: str) -> Tuple[List[str], int]:
    """
    recursive method for getting dot point hierarchies
    """
    relations = []
    while cur_line < len(lines):
        line = lines[cur_line]
        indentation = len(line) - len(line.lstrip())
        if indentation > cur_indent:
            sub_r, new_line = dot_points(lines, cur_line, indentation, lines[cur_line-1])
            relations += sub_r
            cur_line = new_line
        if indentation < cur_indent:
            return relations, cur_line
        if not (line.strip().startswith('-') or line.strip().startswith('*')):
            return relations, cur_line
        if cur_line < len(lines):
            relations.append((lines[cur_line].strip(), head.strip(), 'inside'))
        cur_line += 1
    return relations, cur_line
        
def extract_dot_point_pattern(lines: List[str]) -> List[str]:
    """
    Entry method for gathering dot point hierarchies as relations.
    """
    relations = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        indentation = len(line) - len(line.lstrip())
        if (line.strip().startswith('-') or line.strip().startswith('*')):
            sub_r, new_idx = dot_points(lines, idx, indentation, lines[idx-1])
            relations += sub_r
            idx = new_idx
        idx += 1
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
    relations += extract_dot_point_pattern([l for l in text_as_lines])
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
    text = "".join(lines)
    for r in get_relations(text, lines):
        print(r)
   