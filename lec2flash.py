from flask import Flask

from flask import render_template, request, Response
from entity_extraction import get_relations
from neo4j_work import driver, add_entity, make_match, wipeout, make_match

app = Flask(__name__)

@app.route('/')
def index() -> str:
    return render_template('form.html')

@app.route('/viz')
def viz() -> str:
    return render_template('viz.html')

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
    return render_template('output.html', questions=questions)

@app.route("/download")
def download():
    with driver.session() as session:
        questions = session.write_transaction(make_match)
    export = 'QUESTION\tANSWER\n'
    for question in questions:
        export += f"{question['QUESTION']}\t{question['ANSWER']}\n"
    return Response(
        export,
        mimetype="text/plain",
        headers={"Content-disposition":
                 "attachment; filename=export.txt"})