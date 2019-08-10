import spacy
from spacy import displacy
import re

class Entity():
    def __init__(self, text, head, relation):
        self.text = text
        self.head = head
        self.relation = relation


nlp = spacy.load("en_core_web_lg")

def load_file(filename):
    with open(filename, 'r') as f:
        return f.readlines()

# basic definition checker
def check_def_line(line, symbol):
    split_line = line.split(symbol)
    if (len(split_line) == 2 and split_line[0] and split_line[1]):
        return [(line.split(symbol)[0].strip(), line.split(symbol)[1].strip(), "definition")]
    return []

# recursive method for getting dot point hierarchies
def dot_points(lines, cur_line, cur_indent, head):
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
        
def extract_dot_point_pattern(lines):
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

def extract_defn_pattern(line):
    relations = []
    relations += check_def_line(line, "= ")
    relations += check_def_line(line, "- ")
    relations += check_def_line(line, ": ")
    return relations

def filter_spans(spans):
    # Filter a sequence of spans so they don't contain overlaps
    get_sort_key = lambda span: (span.end - span.start, span.start)
    sorted_spans = sorted(spans, key=get_sort_key, reverse=True)
    result = []
    seen_tokens = set()
    for span in sorted_spans:
        if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
            result.append(span)
            seen_tokens.update(range(span.start, span.end))
    return result

def extract_entity_relations(text):
    doc = nlp(text)
    # Merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    spans = filter_spans(spans)
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)
    relations = []
    for token in filter(lambda w: w.ent_type_, doc):
        if token.dep_ in ("attr", "dobj"):
            subject = [w for w in token.head.lefts if w.dep_ == "nsubj"]
            if subject:
                subject = subject[0]
                relations.append((subject.text.strip(), token.text.strip(), 'object'))
        elif token.dep_ == "pobj" and token.head.dep_ == "prep":
            relations.append((token.head.head.text.strip(), token.text.strip(), 'prep'))
    return relations

def get_relations(text, text_as_lines):
    relations = []
    # get dot point facts
    relations += extract_dot_point_pattern([l for l in text_as_lines])
    # defns
    for l in text_as_lines:
        relations += extract_defn_pattern(l)
    # ai
    relations += extract_entity_relations(text)
    # filter empty relations
    relations = [r for r in relations if r[0] and r[1] and r[2]]
    return relations

if __name__ == "__main__":
    lines = load_file('notes.txt')
    text = "".join(lines)
    for r in get_relations(text, lines):
        print(r)
   