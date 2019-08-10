from flask import Flask

from flask import render_template, request
from entity_extraction import get_relations
from neo4j_work import driver, add_entity, make_match, wipeout, make_match

app = Flask(__name__)

@app.route('/')
def index() -> str:
    return render_template('form.html')

@app.route('/process-file', methods=['POST'])
def process_file() -> str:
    string = request.files['file'].stream.read().decode('utf-8')
    relations = get_relations(string, string.split("\n"))
    with driver.session() as session:
        session.write_transaction(wipeout)
    with driver.session() as session:
        for i in relations:
            session.write_transaction(add_entity, i)
    with driver.session() as session:
        questions = session.write_transaction(make_match)
    # turn this into some html
    html = ''
    #for q in questions:
    #html += f"QUESTION: <p contenteditable='true'> {q['QUESTION']} </p>, ANSWER: {q['ANSWER']}<br></br>"
    return render_template('output.html', questions=questions)
